#include "watchdog.h"
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>
#include <cstdio>

Watchdog::Watchdog(const std::string &device) : fd_(-1), active_(false) {
    fd_ = open(device.c_str(), O_WRONLY);
    if (fd_ < 0) {
        printf("[Watchdog] Cannot open %s (OK if no HW watchdog)\n", device.c_str());
    }
}

Watchdog::~Watchdog() { stop(); }

bool Watchdog::start(unsigned int timeout_s) {
    if (fd_ < 0) return false;
    ioctl(fd_, WDIOC_SETTIMEOUT, &timeout_s);
    active_ = true;
    printf("[Watchdog] Started, timeout=%us\n", timeout_s);
    return true;
}

void Watchdog::kick() {
    if (fd_ >= 0 && active_) {
        write(fd_, "\0", 1);
    }
}

void Watchdog::stop() {
    if (fd_ >= 0) {
        write(fd_, "V", 1);  /* Magic close */
        close(fd_);
        fd_ = -1;
    }
    active_ = false;
}
