import streamlit as st
from datetime import datetime
from hotel_system import Hotel, StandardRoom, DeluxeRoom, ExecutiveSuite

st.set_page_config(page_title="HotelEaseX  - Easy Hotel Management System", page_icon="🏨")
if 'hotel' not in st.session_state:
    st.session_state.hotel = Hotel("Grand Python Hotel", total_rooms=10)
if 'checkout_history' not in st.session_state:
    st.session_state.checkout_history = []

st.title("🏨 HotelEaseX  - Easy Hotel Management System")

room_numbers = [r.room_no for r in st.session_state.hotel.rooms if isinstance(r, (StandardRoom, DeluxeRoom, ExecutiveSuite))]
room_no = st.selectbox("Select Room Number", room_numbers)

def get_room_type_color_and_price(room):
    if isinstance(room, ExecutiveSuite):
        return "Executive Suite", "violet", "₹350/day"
    elif isinstance(room, DeluxeRoom):
        return "Deluxe Room", "cyan", "₹200/day"
    else:
        return "Standard Room", "#90EE90", "₹100/day"

room = next((r for r in st.session_state.hotel.rooms if hasattr(r, 'room_no') and r.room_no == room_no), None)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Room No", room.room_no)
    st.write("Room Status")
    status_color = "crimson" if not room.is_available else "white"
    st.markdown(f"<h2 style='color: {status_color}; padding-top: 0;'>{'Occupied' if not room.is_available else 'Available'}</h2>", unsafe_allow_html=True)
with col2:
    st.metric("Guest Name", room.get_guest() if not room.is_available else "N/A")
    st.write("Room Type")
    room_type, color, _ = get_room_type_color_and_price(room)
    st.markdown(f"<h2 style='color: {color}; padding-top: 0;'>{room_type}</h5>", unsafe_allow_html=True)
with col3:
    st.write("Price")
    _, _, price = get_room_type_color_and_price(room)
    st.markdown(f"<h2 style='padding-top: 0;'>{price}</h2>", unsafe_allow_html=True)

action = st.radio("Choose Action", ("Check In", "Check Out", "Request Cleaning", "Add Amenity"))

if room:
    if action == "Check In":
        guest_name = st.text_input("Guest Name")
        if st.button("Check In"):
            if not room.is_available:
                st.error(f"❌ Room {room_no} is already occupied.")
            elif not guest_name.strip():
                st.warning("⚠️ Guest name cannot be empty.")
            else:
                room.check_in(guest_name)
                st.success(f"✅ Guest {guest_name} checked into Room {room_no}")
                st.balloons()

    elif action == "Check Out":
      if st.button("Check Out"):
          if room.is_available:
              st.error(f"❌ Room {room_no} is already available. No guest to check out.")
          else:
              guest_name = room.get_guest()
              room.check_out()
              st.success(f"✅ Guest **{guest_name}** has successfully checked out from Room {room.room_no}!")
              st.session_state.checkout_history.append({
                  "Guest Name": guest_name,
                  "Room No": room.room_no,
                  "Checkout Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  "Total Bill": room.bill
              })
              st.markdown("<hr style='border: 0; height: 1.5px; background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet);'>", unsafe_allow_html=True)
              st.subheader("💵 Bill Breakdown")
              st.write(f"**Base Room Charges**: ₹{room._last_base_bill}")
              st.write(f"**Cleaning Charges**: ₹{room._last_cleaning_charge}")
              if isinstance(room, DeluxeRoom):
                st.markdown("<b>Amenity Charges:</b>", unsafe_allow_html=True)
                for amenity, price in room.get_amenity_breakdown():
                    st.markdown(f"- {amenity}: ₹{price}")
                st.markdown(f"<p><b>Total Amenity Charges:</b> ₹{room._last_amenity_charges}</p>", unsafe_allow_html=True)
              st.subheader(f"Total: ₹{room.bill}", divider = "rainbow")


    elif action == "Request Cleaning":
        if st.button("Request Cleaning"):
            cost = room.request_cleaning()
            if cost > 0:
                st.success(f"✅ Room cleaned for ₹{cost}")
            else:
                st.info(f"ℹ️ Room {room_no} was already clean.")

    elif action == "Add Amenity":
        if isinstance(room, DeluxeRoom):
            amenity_name = st.text_input("Amenity Name")
            amenity_charge = st.number_input("Amenity Charge (₹)", min_value=0.0, step=5.0)
            if st.button("Add Amenity"):
                if not amenity_name.strip():
                    st.warning("⚠️ Amenity name cannot be empty.")
                else:
                    room.add_amenity(amenity_name, amenity_charge, room_no)
                    st.success(f"✅ Amenity '{amenity_name}' added to Room {room_no}")
        else:
            st.warning("⚠️ Amenities can only be added to Deluxe Rooms or Executive Suites!")


st.subheader("🏢 Room Status Overview")
for r in st.session_state.hotel.rooms[1:]:
    if isinstance(r, (StandardRoom, DeluxeRoom, ExecutiveSuite)):
        status = "Available" if r.is_available else "Occupied"

        if not r.is_available:
            color = "crimson"
        else:
            if isinstance(r, StandardRoom) and not isinstance(r, (DeluxeRoom, ExecutiveSuite)):
                color = "#90EE90"
            elif isinstance(r, ExecutiveSuite):
                color = "violet"
            elif isinstance(r, DeluxeRoom):
                color = "cyan"
            else:
                color = "black"
        if isinstance(r, ExecutiveSuite):
            room_type = "Executive Suite"
            price = "₹350/day"
        elif isinstance(r, DeluxeRoom):
            room_type = "Deluxe Room"
            price = "₹200/day"
        else:
            room_type = "Standard Room"
            price = "₹100/day"

        st.markdown(
            f"<span style='color:{color}; font-size:18px'>Room {r.room_no} - <b>{room_type}</b> ({price}) - {status}</span>",
            unsafe_allow_html=True
        )
if st.session_state.checkout_history:
    st.subheader("🧾 Recent Checkouts")
    st.dataframe(st.session_state.checkout_history, use_container_width=True)
else:
    st.info("No checkouts yet.")