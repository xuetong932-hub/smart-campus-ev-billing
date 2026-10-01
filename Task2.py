"""
Procedural billing prototype for Taylor's Smart Campus EV system.
This program calculates itemised charging bills for campus EV chargers.
It implements tiered pricing, user discounts and additional surcharges.
"""

# Import required library for ceiling rounding
from math import ceil

# --------------------------
# Global constant definitions (PEP8: uppercase for constants)
# Tiered charging rates: AC and DC. Tuple format: (upper_time_limit, hourly_rate)
# float("inf") represents unlimited upper bound for the last pricing tier
CHARGER_RATES = {
    "AC": ((2, 4.00), (4, 6.00), (6, 8.00), (float("inf"), 12.00)),
    "DC": ((2, 10.00), (4, 15.00), (6, 20.00), (float("inf"), 30.00)),
}

# Maximum bill cap for sessions over 6 billable hours
OVERTIME_CAPS = {
    "AC": 80.00,
    "DC": 150.00
}


def calculate_bill(member_type, charger_type, hours,
                   first_time=False, peak=False, idle=False,
                   lost_card=False, eco_pass=False):
    """
    Calculate full itemised EV charging bill.
    :param member_type: user identity: staff / student / visitor
    :param charger_type: charger type: AC or DC
    :param hours: raw decimal charging duration
    :param first_time: boolean flag for first-time user (full waiver)
    :param peak: boolean flag for peak hour surcharge
    :param idle: boolean flag for post-charge idle surcharge
    :param lost_card: boolean flag for RFID card replacement fee
    :param eco_pass: boolean flag for Eco-Pass flat discount
    :return: dictionary containing all bill calculation items (RM currency)
    """
    # Round up to whole hours: any partial hour counts as one full hour
    billable_hours = ceil(hours)
    gross_charge = 0.0
    previous_time_limit = 0

    # Loop through tiered pricing brackets to compute gross charging cost
    for upper_limit, hourly_rate in CHARGER_RATES[charger_type]:
        # Calculate how many hours fall within this price tier
        tier_duration = min(max(billable_hours - previous_time_limit, 0),
                            upper_limit - previous_time_limit)
        gross_charge += tier_duration * hourly_rate
        previous_time_limit = upper_limit
        # Stop loop once all billable hours are accounted for
        if billable_hours <= upper_limit:
            break

    # Apply maximum price cap if billable hours exceed 6 hours
    if billable_hours > 6:
        gross_charge = min(gross_charge, OVERTIME_CAPS[charger_type])

    # Initialise discount variables
    discount_percentage = 0.0
    flat_eco_discount = 0.0
    full_waiver = False

    # Conditional logic for discount rules (if / elif / else)
    if first_time:
        full_waiver = True
    elif member_type == "staff":
        discount_percentage = 0.50
    elif member_type == "student" and charger_type == "AC":
        discount_percentage = 0.25
    else:
        # Visitors receive no percentage discount
        discount_percentage = 0.0

    # Eco pass flat discount only applies to NON-first-time users
    if eco_pass and not first_time:
        flat_eco_discount = 2.00

    # Calculate percentage discount amount
    percentage_discount_amount = gross_charge * discount_percentage

    # First-time user overrides all other discounts
    if full_waiver:
        percentage_discount_amount = gross_charge
        flat_eco_discount = 0.0

    # Subtotal after percentage discount, ensure value cannot be negative
    subtotal_after_discount = max(0.0, gross_charge - percentage_discount_amount)

    # Calculate all surcharge fees
    peak_surcharge = 5.00 if peak else 0.00
    idle_surcharge = 15.00 if idle else 0.00
    rfid_card_fee = 30.00 if lost_card else 0.00
    total_surcharges = peak_surcharge + idle_surcharge + rfid_card_fee

    # Eco discount cannot exceed the total amount before flat discount
    flat_eco_discount = min(flat_eco_discount, subtotal_after_discount + total_surcharges)

    # Final net payable amount
    net_payable = subtotal_after_discount + total_surcharges - flat_eco_discount

    # Return all bill components as dictionary
    return {
        "billable_hours": billable_hours,
        "gross_charge": gross_charge,
        "percentage_discount": percentage_discount_amount,
        "flat_eco_discount": flat_eco_discount,
        "full_waiver": full_waiver,
        "peak_surcharge": peak_surcharge,
        "idle_surcharge": idle_surcharge,
        "rfid_card_fee": rfid_card_fee,
        "net_payable": net_payable
    }


def prompt_yes_no(input_message):
    """
    Helper function to get validated yes/no input from user.
    Returns boolean True for y/yes, False for n/no
    """
    while True:
        user_input = input(f"{input_message} (y/n): ").strip().lower()
        if user_input in ("y", "yes"):
            return True
        elif user_input in ("n", "no"):
            return False
        else:
            print("Invalid input. Please enter y or n only.")


def main():
    """Main program entry point, continuous while loop for multiple billing sessions"""
    print("==== Taylor's Smart Campus EV Billing System ====")
    # Continuous processing while loop
    while True:
        # Collect user and vehicle basic information
        user_id = input("\nEnter User ID: ").strip()
        vehicle_plate = input("Enter Vehicle Number: ").strip().upper()

        # Validate member type input
        while True:
            member_type = input("Member type (staff/student/visitor): ").strip().lower()
            if member_type in ("staff", "student", "visitor"):
                break
            print("Error: Please input staff, student or visitor only.")

        # Validate charger type input
        while True:
            charger_type = input("Charger type (AC/DC): ").strip().upper()
            if charger_type in CHARGER_RATES:
                break
            print("Error: Please input AC or DC only.")

        # Validate charging hours input (must be positive numeric value)
        while True:
            try:
                charging_hours = float(input("Hours charged (>0): "))
                if charging_hours > 0:
                    break
                print("Error: Hours must be greater than zero.")
            except ValueError:
                print("Error: Please enter a valid number.")

        # Get yes/no flags
        is_first_time = prompt_yes_no("First-time registered user")
        has_eco_pass = prompt_yes_no("Certified Green Eco-Pass")
        is_peak_hour = prompt_yes_no("Session during 12 PM–4 PM peak hours")
        has_idle_period = prompt_yes_no("Vehicle remained after fully charged")
        need_card_replacement = prompt_yes_no("Lost RFID card replacement required")

        # Run billing calculation
        final_bill = calculate_bill(member_type, charger_type, charging_hours,
                                    is_first_time, is_peak_hour, has_idle_period,
                                    need_card_replacement, has_eco_pass)

        # Print formatted itemised bill output
        print("\n---------- ITEMIZED EV BILL ----------")
        print(f"User ID / Vehicle Plate: {user_id} / {vehicle_plate}")
        print(f"Charger Type / Billable Hours: {charger_type} / {final_bill['billable_hours']}")
        print(f"Gross Charging Fee:          RM {final_bill['gross_charge']:7.2f}")
        print(f"Member Percentage Discount: -RM {final_bill['percentage_discount']:7.2f}")
        print(f"Eco-Pass Flat Discount:     -RM {final_bill['flat_eco_discount']:7.2f}")
        if final_bill["full_waiver"]:
            print("First-time full waiver:      APPLIED")
        print(f"Peak Hour Surcharge:         RM {final_bill['peak_surcharge']:7.2f}")
        print(f"Idle Time Surcharge:         RM {final_bill['idle_surcharge']:7.2f}")
        print(f"RFID Card Replacement Fee:   RM {final_bill['rfid_card_fee']:7.2f}")
        print(f"==== NET PAYABLE AMOUNT ==== RM {final_bill['net_payable']:7.2f}")

        # Ask whether to start new billing session
        continue_process = prompt_yes_no("\nProcess another vehicle")
        if not continue_process:
            print("\nBilling session closed. Thank you.")
            break


# Execute main function when file runs directly
if __name__ == "__main__":
    main()
