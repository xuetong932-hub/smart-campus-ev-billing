"""
Object‑oriented Smart Campus EV billing application.
This program implements an object‑oriented EV charging billing system for Taylor's Smart Campus.
It demonstrates core OOP principles: Abstraction, Inheritance, Polymorphism and Encapsulation.
Classes: EVCharger, User(abstract base class), MemberUser(concrete subclass), ChargingSession
"""

# ABC and abstractmethod for creating abstract base class and abstract method
from abc import ABC, abstractmethod
# ceil: round‑up charging hours; isfinite: validate numeric input is not infinite/NaN
from math import ceil, isfinite


class EVCharger:
    """
    EVCharger class
    Encapsulates charger properties, tiered‑rate price table and overtime maximum cost cap.
    Responsible for calculating gross charging cost before applying any user‑related discounts.
    """
    # Class‑level constant: tiered charging price rules for AC and DC chargers
    # Tuple format: (upper_time_bound, hourly_rate), float("inf") represents unlimited upper limit
    _RATE_SCHEDULES = {
        "AC": ((2, 4.00), (4, 6.00), (6, 8.00), (float("inf"), 12.00)),
        "DC": ((2, 10.00), (4, 15.00), (6, 20.00), (float("inf"), 30.00)),
    }
    # Class‑level constant: price cap for sessions longer than 6 billable hours
    _OVERTIME_CAPS = {"AC": 80.00, "DC": 150.00}

    def __init__(self, charger_type):
        """
        EVCharger constructor.
        Initialise private charger type field, invoke setter for input validation.
        :param charger_type: str, accepts "AC" or "DC"
        """
        self.__charger_type = "AC"
        self.charger_type = charger_type

    @property
    def charger_type(self):
        """Getter: return private __charger_type value."""
        return self.__charger_type

    @charger_type.setter
    def charger_type(self, value):
        """
        Setter: validate and assign charger type.
        Check input data type, strip whitespace and convert to uppercase.
        Raise TypeError for non‑string input, ValueError if not AC/DC.
        :param value: input charger type string
        """
        if not isinstance(value, str):
            raise TypeError("Charger type must be text: AC or DC.")
        value = value.strip().upper()
        if value not in self._RATE_SCHEDULES:
            raise ValueError("Charger type must be AC or DC.")
        self.__charger_type = value

    def calculate_gross(self, hours):
        """
        Calculate gross charging fee using tiered‑rate pricing logic.
        Partial hours are rounded up to whole billing hours by ceil().
        Applies overtime cost cap for sessions over 6 billable hours.
        :param hours: raw decimal charging duration
        :return: float gross fee before discounts (Malaysian Ringgit)
        """
        hours = float(hours)
        # Reject infinite, NaN or zero/negative time values
        if not isfinite(hours) or hours <= 0:
            raise ValueError("Charging hours must be a positive finite number.")

        billable_hours = ceil(hours)
        gross = 0.0
        lower_limit = 0

        # Iterate through each pricing tier bracket
        for upper_limit, rate in self._RATE_SCHEDULES[self.__charger_type]:
            # Calculate how many hours fall within current price tier
            tier_hours = max(0, min(billable_hours, upper_limit) - lower_limit)
            gross += tier_hours * rate
            lower_limit = upper_limit
            # Early exit loop once all billable hours are processed
            if billable_hours <= upper_limit:
                break

        # Apply maximum price cap when billable hours exceed 6
        if billable_hours > 6:
            gross = min(gross, self._OVERTIME_CAPS[self.__charger_type])
        return gross


class User(ABC):
    """
    Abstract Base Class (ABC) User.
    Defines shared attributes and abstract fee‑calculation interface for all system users.
    Cannot be instantiated directly; must be inherited by concrete subclass MemberUser.
    Demonstrates OOP Abstraction principle.
    """
    def __init__(self, user_id, name, first_time=False):
        """
        User abstract class constructor.
        Initialise private instance fields, use property setters for strict input validation.
        :param user_id: unique user identifier string
        :param name: user full name string
        :param first_time: bool flag for first‑time user full‑waiver benefit
        """
        self.__user_id = ""
        self.__name = ""
        self.__first_time = False
        self.user_id = user_id
        self.name = name
        self.first_time = first_time

    @property
    def user_id(self):
        """Getter: return private user ID value."""
        return self.__user_id

    @user_id.setter
    def user_id(self, value):
        """
        Setter for user_id. Validate data type and non‑empty content.
        :param value: input user id string
        """
        if not isinstance(value, str):
            raise TypeError("User ID must be text.")
        value = value.strip()
        if not value:
            raise ValueError("User ID cannot be empty.")
        self.__user_id = value

    @property
    def name(self):
        """Getter: return private user name value."""
        return self.__name

    @name.setter
    def name(self, value):
        """
        Setter for user name. Validate data type and non‑empty content.
        :param value: input user name string
        """
        if not isinstance(value, str):
            raise TypeError("Name must be text.")
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty.")
        self.__name = value

    @property
    def first_time(self):
        """Getter: return boolean first‑time‑user flag."""
        return self.__first_time

    @first_time.setter
    def first_time(self, value):
        """
        Setter for first‑time flag, enforce boolean type only.
        :param value: bool True / False
        """
        if not isinstance(value, bool):
            raise TypeError("First‑time status must be True or False.")
        self.__first_time = value

    @abstractmethod
    def calculate_fee(self, gross, charger_type):
        """
        Abstract polymorphic method signature.
        Subclasses MUST override and implement this method.
        :param gross: float gross charging fee from charger
        :param charger_type: str "AC" or "DC"
        :return: tuple (percentage_discount, eco‑pass flat discount, waiver boolean flag)
        """


class MemberUser(User):
    """
    MemberUser concrete subclass inheriting from abstract User (IS‑A Inheritance).
    Implements overridden calculate_fee() method to achieve polymorphism.
    Handles discount rules for staff, student, visitor and Eco‑Pass flat discount benefit.
    """
    def __init__(self, user_id, name, member_type="visitor", eco_pass=False,
                 first_time=False):
        """
        MemberUser constructor.
        Call parent User class constructor via super(), initialise member‑specific fields.
        :param user_id: unique user id string
        :param name: user full name string
        :param member_type: str, one of staff / student / visitor
        :param eco_pass: bool flag for certified Green Eco‑Pass
        :param first_time: bool flag for first‑time user full charge waiver
        """
        super().__init__(user_id, name, first_time)
        self.__member_type = "visitor"
        self.member_type = member_type
        self.__eco_pass = False
        self.eco_pass = eco_pass

    @property
    def member_type(self):
        """Getter: return private member type value."""
        return self.__member_type

    @member_type.setter
    def member_type(self, value):
        """
        Setter for member_type. Validate input type and allowed value set.
        :param value: input member‑category string
        """
        if not isinstance(value, str):
            raise TypeError("Member type must be text.")
        value = value.strip().lower()
        if value not in ("staff", "student", "visitor"):
            raise ValueError("Member type must be staff, student, or visitor.")
        self.__member_type = value

    @property
    def eco_pass(self):
        """Getter: return boolean eco‑pass entitlement flag."""
        return self.__eco_pass

    @eco_pass.setter
    def eco_pass(self, value):
        """Setter for eco_pass flag; enforce boolean input only."""
        if not isinstance(value, bool):
            raise TypeError("Eco‑Pass status must be True or False.")
        self.__eco_pass = value

    def calculate_fee(self, gross, charger_type):
        """
        Polymorphic override of abstract base‑class calculate_fee().
        Compute percentage discount, flat eco‑pass discount and full‑waiver flag according to user rules.
        First‑time users receive complete charge waiver, overriding other discounts.
        Staff get 50% discount; students get 25% discount only on AC charger; visitors no percentage discount.
        Eco‑Pass grants RM2 flat discount (ignored for first‑time users).
        :param gross: float gross charging cost
        :param charger_type: str AC / DC
        :return: tuple (percentage_discount, flat_discount, waiver_flag)
        """
        # Polymorphic override: membership determines the percentage discount.
        if self.first_time:
            return gross, 0.0, True
        if self.__member_type == "staff":
            percentage_discount = gross * 0.50
        elif self.__member_type == "student" and charger_type == "AC":
            percentage_discount = gross * 0.25
        else:
            percentage_discount = 0.0

        flat_discount = 2.00 if self.__eco_pass else 0.0
        return percentage_discount, flat_discount, False


class ChargingSession:
    """
    ChargingSession represents one complete EV charging event.
    HAS‑A relationships: contains one User object and one EVCharger object.
    Stores session‑specific data: vehicle plate, charging hours, peak/idle/lost‑card status flags.
    Orchestrates full bill calculation workflow inside generate_bill().
    """
    def __init__(self, user, vehicle_number, charger, hours,
                 peak=False, idle=False, lost_card=False):
        """
        ChargingSession constructor.
        Perform type checking to ensure injected dependencies are correct class instances.
        Use property setters to validate and assign remaining session attributes.
        :param user: MemberUser object reference
        :param vehicle_number: str vehicle registration plate
        :param charger: EVCharger object reference
        :param hours: numeric raw charging duration in hours
        :param peak: bool True if session runs within peak‑hour time window
        :param idle: bool True if vehicle remains connected after fully charged
        :param lost_card: bool True when RFID card replacement fee applies
        """
        if not isinstance(user, User):
            raise TypeError("user must be a User object.")
        if not isinstance(charger, EVCharger):
            raise TypeError("charger must be an EVCharger object.")

        self.__user = user
        self.__charger = charger
        self.__vehicle_number = ""
        self.__hours = 0.0
        self.__peak = False
        self.__idle = False
        self.__lost_card = False

        self.vehicle_number = vehicle_number
        self.hours = hours
        self.peak = peak
        self.idle = idle
        self.lost_card = lost_card

    def get_user(self):
        """Accessor method: return encapsulated User instance reference."""
        return self.__user

    def set_user(self, user):
        """Mutator method: assign new User instance with type validation."""
        if not isinstance(user, User):
            raise TypeError("user must be a User object.")
        self.__user = user

    def get_charger(self):
        """Accessor method: return encapsulated EVCharger instance reference."""
        return self.__charger

    def set_charger(self, charger):
        """Mutator method: assign new EVCharger instance with type validation."""
        if not isinstance(charger, EVCharger):
            raise TypeError("charger must be an EVCharger object.")
        self.__charger = charger

    @property
    def vehicle_number(self):
        """Getter: return vehicle registration plate string."""
        return self.__vehicle_number

    @vehicle_number.setter
    def vehicle_number(self, value):
        """Setter: validate vehicle plate input, convert to uppercase, disallow empty value."""
        if not isinstance(value, str):
            raise TypeError("Vehicle number must be text.")
        value = value.strip().upper()
        if not value:
            raise ValueError("Vehicle number cannot be empty.")
        self.__vehicle_number = value

    @property
    def hours(self):
        """Getter: return raw session charging hours value."""
        return self.__hours

    @hours.setter
    def hours(self, value):
        """
        Setter for charging hours.
        Convert input to float; catch conversion errors; reject non‑positive or infinite values.
        """
        try:
            value = float(value)
        except (TypeError, ValueError) as error:
            raise TypeError("Charging hours must be numeric.") from error

        if not isfinite(value) or value <= 0:
            raise ValueError("Charging hours must be a positive finite number.")
        self.__hours = value

    @property
    def peak(self):
        """Getter: return peak‑hour boolean flag."""
        return self.__peak

    @peak.setter
    def peak(self, value):
        """Setter: enforce boolean type for peak flag."""
        if not isinstance(value, bool):
            raise TypeError("Peak status must be True or False.")
        self.__peak = value

    @property
    def idle(self):
        """Getter: return idle‑after‑charge boolean flag."""
        return self.__idle

    @idle.setter
    def idle(self, value):
        """Setter: enforce boolean type for idle flag."""
        if not isinstance(value, bool):
            raise TypeError("Idle status must be True or False.")
        self.__idle = value

    @property
    def lost_card(self):
        """Getter: return lost‑RFID‑card boolean flag."""
        return self.__lost_card

    @lost_card.setter
    def lost_card(self, value):
        """Setter: enforce boolean type for lost‑card flag."""
        if not isinstance(value, bool):
            raise TypeError("Lost‑card status must be True or False.")
        self.__lost_card = value

    def get_peak(self):
        """Alternative accessor method for peak status."""
        return self.__peak

    def set_peak(self, value):
        """Alternative mutator method for peak status, reuse property setter logic."""
        self.peak = value

    def get_idle(self):
        """Alternative accessor method for idle status."""
        return self.__idle

    def set_idle(self, value):
        """Alternative mutator method for idle status, reuse property setter logic."""
        self.idle = value

    def get_lost_card(self):
        """Alternative accessor method for lost‑card status."""
        return self.__lost_card

    def set_lost_card(self, value):
        """Alternative mutator method for lost‑card status, reuse property setter logic."""
        self.lost_card = value

    def generate_bill(self):
        """
        Main business logic method to compute complete itemised bill.
        Workflow:
        1. Call EVCharger.calculate_gross() to get base charging cost
        2. Polymorphic call to user.calculate_fee() to resolve discounts and waiver
        3. Apply surcharges for peak hour, idle time and RFID card replacement
        4. Compute subtotal, cap flat discount to prevent negative payment
        5. Return dictionary containing every item of the final bill
        :return: dict full structured bill data
        """
        charger_type = self.__charger.charger_type
        gross = self.__charger.calculate_gross(self.__hours)

        # Polymorphic method call: runtime executes MemberUser implementation
        percentage_discount, flat_discount, waiver = self.__user.calculate_fee(
            gross, charger_type)

        # First‑time full waiver invalidates eco‑pass flat discount
        if waiver:
            flat_discount = 0.0

        # Define fixed additional surcharge fees
        peak_fee = 5.00 if self.peak else 0.0
        idle_fee = 15.00 if self.idle else 0.0
        card_fee = 30.00 if self.lost_card else 0.0

        # Subtract percentage discount, ensure value cannot drop below zero
        before_flat = max(0.0, gross - percentage_discount)
        surcharge_items = [peak_fee, idle_fee, card_fee]
        before_flat += sum(surcharge_items)

        # Prevent flat discount from making payable amount negative
        flat_discount = min(flat_discount, before_flat)
        net = before_flat - flat_discount

        return {
            "user": self.__user, "vehicle": self.__vehicle_number,
            "charger": charger_type, "hours": ceil(self.__hours),
            "gross": gross, "percentage_discount": percentage_discount,
            "flat_discount": flat_discount, "waiver": waiver,
            "peak_surcharge": peak_fee, "idle_surcharge": idle_fee,
            "card_fee": card_fee, "net": net,
        }


def print_bill(bill):
    """
    Helper utility function.
    Format and print human‑readable itemised EV charging bill onto console output.
    :param bill: dict result object returned from ChargingSession.generate_bill()
    """
    user = bill["user"]
    print("\n--- ITEMIZED EV BILL ---")
    print(f"User / vehicle: {user.user_id} - {user.name} / {bill['vehicle']}")
    print(f"Charger / billable hours: {bill['charger']} / {bill['hours']}")
    print(f"Gross charging fee:          RM {bill['gross']:7.2f}")
    print(f"Member discount:            -RM {bill['percentage_discount']:7.2f}")
    print(f"Eco‑Pass discount:          -RM {bill['flat_discount']:7.2f}")
    if bill["waiver"]:
        print("First‑time waiver:           applied")
    print(f"Peak‑hour surcharge:         RM {bill['peak_surcharge']:7.2f}")
    print(f"Idle surcharge:              RM {bill['idle_surcharge']:7.2f}")
    print(f"RFID replacement fee:        RM {bill['card_fee']:7.2f}")
    print(f"NET PAYABLE:                 RM {bill['net']:7.2f}")


def demo():
    """
    Demonstration function to test object‑oriented implementation with two sample scenarios.
    Scenario 1: Staff user with Eco‑Pass, AC charger, peak hour surcharge + lost RFID card fee.
    Scenario 2: First‑time visitor user, DC charger, idle‑after‑charge surcharge.
    Shows polymorphism: different user types invoke different discount calculation logic.
    """
    # User and MemberUser show polymorphic calculation for distinct user types.
    staff = MemberUser("T100", "Amin", "staff", eco_pass=True)
    staff_session = ChargingSession(
        staff, "ABC1234", EVCharger("AC"), 3, peak=True, lost_card=True)
    print_bill(staff_session.generate_bill())

    first_time_visitor = MemberUser("V205", "Mei", first_time=True)
    visitor_session = ChargingSession(
        first_time_visitor, "WXY7788", EVCharger("DC"), 7.5, idle=True)
    print_bill(visitor_session.generate_bill())


if __name__ == "__main__":
    # Program entry‑point: execute demo test cases only when this file runs directly
    demo()
