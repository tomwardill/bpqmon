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

## Contributing

Feel free to fork/patch/submit PRs or open Issues

