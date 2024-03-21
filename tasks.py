from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    orders = get_orders()

    page = browser.page()
    for order in orders:
        close_annoying_modal(page)
        fill_the_form(order, page)

        pdf = PDF()
        pdf_file = store_receipt_as_pdf(order['Order number'], page, pdf)
        screenshot_path = screenshot_robot(order['Order number'], page)
        embed_screenshot_to_receipt(screenshot_path, pdf_file, pdf)

        page.click("button:text('ORDER ANOTHER ROBOT')")

    archive_receipts()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal(page):
    page = browser.page()
    page.click("button:text('Yep')")


def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    library = Tables()
    orders = library.read_table_from_csv("orders.csv")

    return orders

def fill_the_form(row, page):
    page.select_option("#head", row['Head'])
    page.click(f"#id-body-{row['Body']}")

    page.fill(".form-control", row['Legs'])
    page.fill("#address", row['Address'])
    page.click("button:text('Preview')")
    page.click("button:text('ORDER')")
    while "alert-danger" in page.content():
        page.click("button:text('ORDER')")

def store_receipt_as_pdf(order_number, page, pdf):
    order_receipt = page.locator("#parts").inner_html()
    path = f"output/receipts/order_{order_number}.pdf"

    pdf.html_to_pdf(order_receipt, path)

    return path

def screenshot_robot(order_number, page):
    path = f"output/screenshots/order_{order_number}.png"
    page.screenshot(path=path)

    return path

def embed_screenshot_to_receipt(screenshot, pdf_file, pdf):
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("output/receipts", "output/receipts.zip")

    
    
