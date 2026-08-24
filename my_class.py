class Customer:
    def __init__(self, customer_id, name, member_type="General"):
        self.customer_id = customer_id
        self.name = name
        self.member_type = member_type
        self.points = 0

    def get_discount_rate(self, promo_discount_rate=0.0):
        member_discounts = {"General": 0.0, "Student": 0.20, "VIP": 0.30}
        member_rate = member_discounts.get(self.member_type, 0.0)
        return max(member_rate, promo_discount_rate)

    def add_points(self, net_price):
        earned = int(net_price // 10)
        self.points += earned
        return earned


class Showtime:
    def __init__(self, showtime_id, movie_name, theater_no, start_time, end_time, base_price):
        self.showtime_id = showtime_id
        self.movie_name = movie_name
        self.theater_no = theater_no
        self.start_time = start_time
        self.end_time = end_time
        self.base_price = base_price


class Booking:
    def __init__(self, booking_id, customer, showtime, seat_number, seat_type):
        self.booking_id = booking_id
        self.customer = customer
        self.showtime = showtime
        self.seat_number = seat_number.upper()
        self.seat_type = seat_type
        self.booking_time = datetime.now()
        self.status = "Pending"
        # เรียกใช้ Helper Function คิดราคา
        self.net_price = calculate_booking_price(showtime.base_price, seat_type, customer.member_type)

    def check_timeout(self):
        if self.status == "Pending":
            if datetime.now() > self.booking_time + timedelta(minutes=10):
                self.status = "Cancelled"
                return True
        return False

    def confirm_payment(self):
        if self.check_timeout():
            raise Exception("เกินเวลา 10 นาที (Timeout Auto-Cancel)")
        self.status = "Paid"
        self.customer.add_points(self.net_price)
        return self.net_price

# Helper Functions
def calculate_booking_price(base_price, seat_type="Normal", member_type="General", promo_discount=0.0):
    """ฟังก์ชันที่ 1: คำนวณราคาสุทธิ (มี Default Argument)"""
    seat_extras = {"Normal": 0, "Deluxe": 40, "Honeymoon": 80, "VIP": 190}
    member_discounts = {"General": 0.0, "Student": 0.20, "VIP": 0.30}

    total_seat_price = base_price + seat_extras.get(seat_type, 0)
    best_discount = max(member_discounts.get(member_type, 0.0), promo_discount)
    return round(total_seat_price * (1 - best_discount), 2)


def validate_seat_booking(seat_number, existing_seats_list, valid_seat_range=None):
    """ฟังก์ชันที่ 2: ตรวจสอบผังและที่นั่งซ้ำ (มี Default Argument)"""
    if valid_seat_range is None:
        valid_seat_range = [f"{row}{num}" for row in "ABCDEF" for num in range(1, 11)]

    seat_upper = seat_number.upper()
    if seat_upper not in valid_seat_range:
        return False, f"ที่นั่ง {seat_number} ไม่มีอยู่ในระบบ (Invalid Seat)"
    if seat_upper in existing_seats_list:
        return False, f"ที่นั่ง {seat_number} ถูกจองแล้ว (Double Booking)"
    return True, "ที่นั่งว่าง สามารถจองได้"


def process_ticket_scan(ticket_id, current_status="Paid", auto_update=True):
    """ฟังก์ชันที่ 3: จำลองการสแกน QR Code เข้าโรง (มี Default Argument)"""
    if current_status == "Used":
        return False, f"ตั๋ว {ticket_id} ถูกใช้งานไปแล้ว ไม่สามารถสแกนซ้ำได้!"
    elif current_status != "Paid":
        return False, f"ตั๋ว {ticket_id} ยังไม่ได้ชำระเงิน"

    new_status = "Used" if auto_update else current_status
    return True, f"สแกนสำเร็จ! ยินดีต้อนรับเข้าสู่โรงภาพยนตร์ ({new_status})"



# Execution Simulation Loop (จำลอง 300 รายการทีละคน)

showtime_1 = Showtime(
    "ST01",
    "Avatar 3",
    1,
    datetime(2026, 8, 20, 14, 0),
    datetime(2026, 8, 20, 17, 0),
    160,
)
showtime_2 = Showtime(
    "ST02",
    "Spider-Man",
    2,
    datetime(2026, 8, 20, 15, 30),
    datetime(2026, 8, 20, 18, 0),
    180,
)
showtime_3 = Showtime(
    "ST03",
    "Batman",
    3,
    datetime(2026, 8, 20, 19, 0),
    datetime(2026, 8, 20, 22, 0),
    200,
)

showtimes_pool = [showtime_1, showtime_2, showtime_3]

# แยกเก็บรายการที่นั่งที่ถูกจองแล้วของแต่ละโรง (ป้องกันการจองชนกันข้ามโรง)
booked_seats_by_theater = {1: [], 2: [], 3: []}

all_bookings = []
member_pool = ["General", "Student", "VIP"]
seat_type_pool = ["Normal", "Deluxe", "Honeymoon", "VIP"]
seat_pool = [f"{r}{n}" for r in "ABCDEF" for n in range(1, 11)] + ["Z99"]


# Loop จำลอง 300 รายการ (สุ่มเลือกโรงภาพยนตร์)

for i in range(1, 301):
    cust_id = f"C{i:03d}"
    cust_name = f"Customer_{i}"
    chosen_member = random.choice(member_pool)
    chosen_seat = random.choice(seat_pool)
    chosen_seat_type = random.choice(seat_type_pool)
    booking_id = f"BK{i:03d}"

    # สุ่มเลือกโรงภาพยนตร์ 1 จาก 3 โรง
    chosen_showtime = random.choice(showtimes_pool)
    theater_no = chosen_showtime.theater_no

    customer = Customer(cust_id, cust_name, chosen_member)

    # ตรวจสอบที่นั่งซ้ำเฉพาะในโรงภาพยนตร์ที่เลือก
    is_valid, seat_msg = validate_seat_booking(
        chosen_seat, booked_seats_by_theater[theater_no]
    )

    if not is_valid:
        failed_booking = Booking(
            booking_id,
            customer,
            chosen_showtime,
            chosen_seat,
            chosen_seat_type,
        )
        failed_booking.status = f"Rejected ({seat_msg})"
        failed_booking.net_price = 0.0
        all_bookings.append(failed_booking)
        continue

    try:
        new_booking = Booking(
            booking_id,
            customer,
            chosen_showtime,
            chosen_seat,
            chosen_seat_type,
        )

        if random.random() < 0.10:
            new_booking.booking_time = datetime.now() - timedelta(minutes=15)

        new_booking.confirm_payment()
        booked_seats_by_theater[theater_no].append(
            chosen_seat
        ) 
        all_bookings.append(new_booking)

    except Exception:
        new_booking.net_price = 0.0
        all_bookings.append(new_booking)
