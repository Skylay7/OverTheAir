from PIL import ImageGrab


def take_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    screenshot.close()
    with open("screenshot.png", "rb") as screenshot_file:
        screenshot_data = screenshot_file.read()
    return screenshot_data


print(take_screenshot())
