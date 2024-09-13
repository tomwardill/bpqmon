# BPQMON

A small tool for monitoring linBPQ / BPQ32 output via the IP/Telnet interface

This project is still under development and is not stable or have pretty much any features right now.

## Goal

A simple CLI application that can connect to a linbpq instance using the telnet port and output the monitoring data in a variety of ways:

* Pretty CLI terminal app
* Plain terminal output
* Log file output
* MQTT output

## Installation

This project is not currently published to PyPi, you have to use the checkout for now.

It uses [poetry](https://python-poetry.org/docs/#installation) for dependency management

```
poetry install
```

## Running

Run the application using poetry and pass some command line options

```
poetry run bpqmon --host localhost --port 8011 --username <bpq login name> --password <bpq login password>
```

This should open a CLI application, connect to the linbpq instance, and start outputting monitoring

## Usage

There are a few options that are available:

| CLI Flag | Purpose |
| - | - |
| `--host` | LinBPQ host name/IP, can be `localhost` |
| `--port` | LinBPQ host port, usually `8011` |
| `--plain-terminal` | Plain text output, exclusive with `--fancy-terminal` |
| `--fancy-terminal` | Fancy coloured and scrolling terminal, exclusive with `--plain-terminal` |
| `--username` | Username for BPQ Telnet interface |
| `--password` | Password for BPQ Telnet interface |
| `--mqtt` | Enable MQTT output |
| `--mqtt-hostname` | Hostname/IP of MQTT server |
| `--mqtt-port` | Port of MQTT Server |
| `--mqtt-username` | Username for MQTT Server |
| `--mqtt-password` | Password for MQTT Server |

## MQTT Output

MQTT will be output to the following topics:

| Topic | Content |
| - | - |
| `bpq/log` | BPQ 'System' level output, connection strings, etc |
| `bpq/port/<x>` | Packets on the appropriate port number |

I'd suggest using [MQTT Scroller](https://github.com/ucl-casa-ce/Galactic-Unicorn-MQTT-Scroller) on a [Galatic Unicorn](https://shop.pimoroni.com/products/space-unicorns?variant=40842033561683) if you want a fancy display.

## Contributing

Feel free to fork/patch/submit PRs or open Issues

