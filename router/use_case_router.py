from handlers.brandwall import handle as brand_wall
from handlers.main_signage import handle as main_signage
from handlers.tyre_display import handle as tyre_display
from handlers.customer_lounge import handle as customer_lounge
from handlers.workshop import handle as workshop

USE_CASE_ROUTER = {
    "brand_wall": brand_wall,
    "main_signage": main_signage,
    "tyre_display_area": tyre_display,
    "customer_lounge": customer_lounge,
    "workshop": workshop,
}
