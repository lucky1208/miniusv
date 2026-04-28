/**
 * CAN Bus Interface Implementation (SocketCAN)
 *
 * Linux SocketCAN based CAN communication for i.MX8 FlexCAN.
 */

#include "can_interface.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <time.h>

/* Get monotonic time in microseconds */
static uint64_t get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)ts.tv_nsec / 1000ULL;
}

/* RX thread function */
static void *can_rx_thread(void *arg) {
    CANInterface *can = (CANInterface *)arg;
    struct can_frame linux_frame;
    CANFrame app_frame;

    while (can->rx_running) {
        int n = read(can->socket_fd, &linux_frame, sizeof(linux_frame));
        if (n < 0) {
            if (errno == EINTR || errno == EAGAIN) continue;
            can->error_count++;
            continue;
        }

        /* Convert Linux CAN frame to app frame */
        app_frame.can_id = linux_frame.can_id & CAN_EFF_MASK;
        app_frame.dlc = linux_frame.can_dlc;
        memcpy(app_frame.data, linux_frame.data, linux_frame.can_dlc);
        app_frame.timestamp = get_time_us();

        can->rx_count++;

        /* Call user callback */
        if (can->rx_callback) {
            can->rx_callback(&app_frame, can->rx_user_data);
        }
    }

    return NULL;
}

int can_init(CANInterface *can, const char *ifname, uint32_t bitrate) {
    struct sockaddr_can addr;
    struct ifreq ifr;

    memset(can, 0, sizeof(CANInterface));
    strncpy(can->ifname, ifname, sizeof(can->ifname) - 1);

    /* Create SocketCAN socket */
    can->socket_fd = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (can->socket_fd < 0) {
        perror("CAN socket create failed");
        return -1;
    }

    /* Bind to interface */
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_name[IFNAMSIZ - 1] = '\0';
    if (ioctl(can->socket_fd, SIOCGIFINDEX, &ifr) < 0) {
        perror("CAN interface index failed");
        close(can->socket_fd);
        return -2;
    }

    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(can->socket_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("CAN bind failed");
        close(can->socket_fd);
        return -3;
    }

    /* Enable loopback (for self-test) */
    int loopback = 1;
    setsockopt(can->socket_fd, SOL_CAN_RAW, CAN_RAW_LOOP_BACK,
               &loopback, sizeof(loopback));

    can->is_open = true;
    printf("[CAN] Initialized on %s (bitrate: %u)\n", ifname, bitrate);
    return 0;
}

void can_close(CANInterface *can) {
    if (!can->is_open) return;

    can->rx_running = false;
    if (can->rx_thread) {
        pthread_join(can->rx_thread, NULL);
    }

    if (can->socket_fd >= 0) {
        close(can->socket_fd);
        can->socket_fd = -1;
    }

    can->is_open = false;
    printf("[CAN] Closed %s\n", can->ifname);
}

int can_send(CANInterface *can, const CANFrame *frame) {
    if (!can->is_open) return -1;

    struct can_frame linux_frame;
    memset(&linux_frame, 0, sizeof(linux_frame));

    linux_frame.can_id = frame->can_id;
    linux_frame.can_dlc = frame->dlc;
    memcpy(linux_frame.data, frame->data, frame->dlc);

    int n = write(can->socket_fd, &linux_frame, sizeof(linux_frame));
    if (n < 0) {
        can->error_count++;
        return -2;
    }

    can->tx_count++;
    return 0;
}

int can_receive(CANInterface *can, CANFrame *frame, int timeout_ms) {
    if (!can->is_open) return -1;

    /* Set timeout */
    if (timeout_ms >= 0) {
        struct timeval tv;
        tv.tv_sec = timeout_ms / 1000;
        tv.tv_usec = (timeout_ms % 1000) * 1000;
        setsockopt(can->socket_fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    }

    struct can_frame linux_frame;
    int n = read(can->socket_fd, &linux_frame, sizeof(linux_frame));
    if (n < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) return -2;  /* timeout */
        can->error_count++;
        return -3;
    }

    frame->can_id = linux_frame.can_id & CAN_EFF_MASK;
    frame->dlc = linux_frame.can_dlc;
    memcpy(frame->data, linux_frame.data, linux_frame.can_dlc);
    frame->timestamp = get_time_us();

    can->rx_count++;
    return 0;
}

int can_set_rx_callback(CANInterface *can, CANRxCallback callback, void *user_data) {
    can->rx_callback = callback;
    can->rx_user_data = user_data;
    can->rx_running = true;

    if (pthread_create(&can->rx_thread, NULL, can_rx_thread, can) != 0) {
        can->rx_running = false;
        return -1;
    }

    return 0;
}

int can_add_filter(CANInterface *can, uint32_t id, uint32_t mask) {
    if (!can->is_open) return -1;

    struct can_filter rfilter;
    rfilter.can_id = id;
    rfilter.can_mask = mask;

    return setsockopt(can->socket_fd, SOL_CAN_RAW, CAN_RAW_FILTER,
                      &rfilter, sizeof(rfilter));
}

void can_get_stats(CANInterface *can, uint32_t *tx, uint32_t *rx, uint32_t *errors) {
    if (tx) *tx = can->tx_count;
    if (rx) *rx = can->rx_count;
    if (errors) *errors = can->error_count;
}
