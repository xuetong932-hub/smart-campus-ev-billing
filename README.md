# Smart Campus EV Charging Billing System

A Python coursework project that calculates itemised electric vehicle charging bills for a fictional university campus. It presents two implementations of the same billing rules: a procedural command-line program and an object-oriented demonstration.

## Implementations

| File | Approach | How it runs |
| --- | --- | --- |
| `Task2.py` | Procedural Python with tiered pricing, input validation, discounts, surcharges, and a repeat-session loop | Interactive prompts in the terminal |
| `Task4.py` | Object-oriented Python using an abstract `User`, a `MemberUser`, an `EVCharger`, and a `ChargingSession` | Prints two sample billing scenarios |

## Requirements

- Python 3.8 or newer
- No third-party packages

## Run

Open a terminal in this folder and run either program:

```bash
python Task2.py
```

```bash
python Task4.py
```

On some systems, use `python3` instead of `python`.

## Billing rules represented

- AC and DC charging use separate hourly tiers. Partial hours are rounded up.
- Sessions longer than six billable hours have a charger-specific maximum charge.
- Staff receive a percentage discount; students receive a percentage discount on AC sessions; first-time users receive a charging-fee waiver.
- Eco-Pass and peak-hour, idle-time, and lost-card charges are included.
- Currency amounts are shown in Malaysian ringgit (RM).

These are the rules stated in the coursework brief and are illustrative; this program is not connected to a real charging network or payment service.

## Project structure

```text
smart-campus-ev-billing/
├── README.md
├── Task2.py
├── Task4.py
└── .gitignore
```

## Notes

This repository contains coursework-style examples, not production billing software. In `Task4.py`, membership categories are handled within `MemberUser`; the program does not define separate staff, student, and visitor subclasses. The original source files are retained as supplied. Please review your institution's rules before publishing assessed work, and do not upload the assessment document or personal/course submission material.

## Repository topics

`python` `object-oriented-programming` `procedural-programming` `billing-system` `coursework`
