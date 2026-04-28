#ifndef WATCHDOG_H
#define WATCHDOG_H

#include <cstdint>
#include <string>

class Watchdog {
public:
    Watchdog(const std::string &device = "/dev/watchdog");
    ~Watchdog();
    bool start(unsigned int timeout_s);
    void kick();
    void stop();
private:
    int fd_;
    bool active_;
};

#endif
