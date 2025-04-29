from time import sleep
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class BillingMixin:
    """Mixin that provides billing functionality"""
    def calculate_base_bill(self, rate_per_day):
        days_stayed = (self._check_out_time - self._check_in_time).days + 1
        return days_stayed * rate_per_day

class CleaningService:
    """Mixin for room cleaning services"""
    def __init__(self):
        self.cleaning_fee = 25.0
        self.is_cleaned = True

    def request_cleaning(self):
        if not self.is_cleaned:
            print(f"Room {self.room_no} has been cleaned.")
            self.is_cleaned = True
            return self.cleaning_fee
        else:
            print(f"Room {self.room_no} is already clean.")
            return 0

class AmenityProvider:
    def __init__(self):
        self.amenities = []
        self.amenity_charges = 0.0

    def add_amenity(self, amenity, charge, room_no):
        self.amenities.append((amenity, charge))
        self.amenity_charges += charge
        print(f"Added {amenity} to room no {room_no} for ${charge}")

    def get_amenity_charges(self):
        return self.amenity_charges

    def get_amenity_breakdown(self):
        return self.amenities

class Hotel:
    def __init__(self, hotel_name: str, total_rooms: int):
        self.hotel_name = hotel_name
        self.total_rooms = total_rooms
        self.rooms = []

        for room_no in range(total_rooms + 1):
            if room_no == 0:
                self.rooms.append("Laundry Room")
            elif room_no % 5 == 0:
                self.rooms.append(ExecutiveSuite(self, room_no))
            elif room_no % 3 == 0:
                self.rooms.append(DeluxeRoom(self, room_no))
            else:
                self.rooms.append(StandardRoom(self, room_no))

    def __add__(self, other):
        if isinstance(other, Room):
            self.rooms.append(other)
            return self
        else:
            raise TypeError("Can only add Room instances to Hotel.")

class Room(ABC):
    def __init__(self, hotel: Hotel, room_no: int):
        self.hotel = hotel
        self.room_no = room_no
        self.is_available = True
        self.__guest = None
        self._check_in_time = None
        self._check_out_time = None
        self.__aadhar = None
        self.__phone = None
        self.bill = 0.0
        self._last_base_bill = 0.0
        self._last_cleaning_charge = 0.0
        self._last_amenity_charges = 0.0

    @abstractmethod
    def calculate_bill(self):
        pass

    def get_guest(self):
        return self.__guest

    def get_aadhar(self):
        return self.__aadhar

    def get_phone(self): 
        return self.__phone

    def check_in(self, guest_name: str, check_in_time: datetime = datetime.now(), aadhar: str = None, phone: str = None):
        if not self.is_available:
            print(f"Room {self.room_no} is already occupied by {self.__guest}.")
        else:
            self.is_available = False
            self.__guest = guest_name
            self._check_in_time = check_in_time
            self.__aadhar = aadhar
            self.__phone = phone
            print(f"Guest {guest_name} checked into room {self.room_no} at {check_in_time}.")

    def check_out(self, check_out_time: datetime = datetime.now()):
        if self.is_available:
            print(f"Room {self.room_no} is already available.")
            return None
        else:
            self.is_available = True
            guest_name = self.__guest
            print(f"Guest {guest_name} checked out of room {self.room_no}.")
            self.__guest = None
            self._check_out_time = check_out_time
            self._last_base_bill = self.calculate_base_bill(self.rate_per_day)
            self._last_cleaning_charge = 0 if self.is_cleaned else self.cleaning_fee
            if isinstance(self, DeluxeRoom):
                self._last_amenity_charges = self.get_amenity_charges()
            else:
                self._last_amenity_charges = 0.0
            self.bill = self._last_base_bill + self._last_cleaning_charge + self._last_amenity_charges
            self._check_in_time = None
            self._check_out_time = None

class StandardRoom(Room, BillingMixin, CleaningService):
    def __init__(self, hotel, room_no):
        Room.__init__(self, hotel, room_no)
        CleaningService.__init__(self)
        self.rate_per_day = 100

    def calculate_bill(self):
        base_bill = self.calculate_base_bill(self.rate_per_day)
        cleaning_charge = 0 if self.is_cleaned else self.cleaning_fee
        return base_bill + cleaning_charge

class DeluxeRoom(Room, BillingMixin, CleaningService, AmenityProvider):
    def __init__(self, hotel, room_no):
        Room.__init__(self, hotel, room_no)
        CleaningService.__init__(self)
        AmenityProvider.__init__(self)
        self.rate_per_day = 200
        self.add_amenity("Mini Bar", 50, room_no)
        self.add_amenity("Premium TV", 25, room_no)

    def calculate_bill(self):
        base_bill = self.calculate_base_bill(self.rate_per_day)
        cleaning_charge = 0 if self.is_cleaned else self.cleaning_fee
        amenity_charges = self.get_amenity_charges()
        print(f"Base bill: {base_bill}, Cleaning: {cleaning_charge}, Amenities: {amenity_charges}")
        return base_bill + cleaning_charge + amenity_charges

class ExecutiveSuite(DeluxeRoom):
    def __init__(self, hotel, room_no):
        super().__init__(hotel, room_no)
        self.rate_per_day = 350
        self.add_amenity("Jacuzzi", 100, room_no)
        self.add_amenity("Personal Butler", 150, room_no)

def main():
    grand_hotel = Hotel("Grand Hotel", 10)
    deluxe_room = DeluxeRoom(grand_hotel, 11)
    executive_suite = ExecutiveSuite(grand_hotel, 12)
    grand_hotel += deluxe_room
    grand_hotel += executive_suite

    now = datetime.now()
    grand_hotel.rooms[1].check_in("John Smith", now - timedelta(days=2))
    grand_hotel.rooms[2].check_in("Jane Doe", now - timedelta(days=3))
    grand_hotel.rooms[11].check_in("VIP Guest", now - timedelta(days=1))
    grand_hotel.rooms[12].check_in("Executive Guest", now - timedelta(days=2))

    grand_hotel.rooms[1].is_cleaned = False
    grand_hotel.rooms[11].add_amenity("Room Service", 75, 11)

    grand_hotel.rooms[1].check_out()
    grand_hotel.rooms[2].check_out()
    grand_hotel.rooms[11].check_out()
    grand_hotel.rooms[12].check_out()

if __name__ == "__main__":
    main()