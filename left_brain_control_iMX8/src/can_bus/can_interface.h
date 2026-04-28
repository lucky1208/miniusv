/**
 * CAN Bus Interface for USV Right Brain
 *
 * SocketCAN interface for communication with:
 * - ESC motor controllers (CAN ID: 0x200-0x20F)
 * - BMS (CAN ID: 0x300-0x30F)
 * - GPS/INS (CAN ID: 0x400-0x40F)
 *
 * i.MX8 has native FlexCAN controller support via SocketCAN.
 */

#ifndef CAN_INTERFACE_H
#define CAN_INTERFACE_H

#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

#ifdef __cplusplus
extern "C" {
#endif

#define CAN_MAX_DLC 8
#define CAN_MAX_FRAME_SIZE 16

/* CAN frame structure (compatible with Linux socketcan) */
typedef struct {
    uint32_t can_id;     /* CAN ID (11-bit or 29-bit) */
    uint8_t  dlc;        /* Data Length Code (0-8) */
    uint8_t  data[8];    /* Data bytes */
    uint64_t timestamp;  /* microseconds */
} CANFrame;

/* CAN filter for receive */
typedef struct {
    uint32_t id;
    uint32_t mask;
} CANFilter;

/* Callback for received CAN frames */
typedef void (*CANRxCallback)(const CANFrame *frame, void *user_data);

/* CAN interface handle */
typedef struct {
    int socket_fd;
    char ifname[16];
    bool is_open;
    bool use_fd;           /* CAN-FD support */
    CANRxCallback rx_callback;
    void *rx_user_data;
    pthread_t rx_thread;
    bool rx_running;
    uint32_t tx_count;
    uint32_t rx_count;
    uint32_t error_count;
} CANInterface;

/**
 * Initialize CAN interface
 * @param can CAN interface handle
 * @param ifname Interface name (e.g., "can0")
 * @param bitrate CAN bitrate (e.g., 500000)
 * @return 0 on success, negative on error
 */
int can_init(CANInterface *can, const char *ifname, uint32_t bitrate);

/**
 * Close CAN interface
 */
void can_close(CANInterface *can);

/**
 * Send CAN frame
 * @return 0 on success, negative on error
 */
int can_send(CANInterface *can, const CANFrame *frame);

/**
 * Receive CAN frame (blocking with timeout)
 * @param timeout_ms Timeout in milliseconds (-1 = blocking)
 * @return 0 on success, negative on error/timeout
 */
int can_receive(CANInterface *can, CANFrame *frame, int timeout_ms);

/**
 * Set receive callback (starts RX thread)
 */
int can_set_rx_callback(CANInterface *can, CANRxCallback callback, void *user_data);

/**
 * Add CAN filter for receive
 */
int can_add_filter(CANInterface *can, uint32_t id, uint32_t mask);

/**
 * Get statistics
 */
void can_get_stats(CANInterface *can, uint32_t *tx, uint32_t *rx, uint32_t *errors);

#ifdef __cplusplus
}
#endif

#endif /* CAN_INTERFACE_H */
