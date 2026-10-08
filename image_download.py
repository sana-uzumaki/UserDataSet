import os
import io
import requests
from PIL import Image
import cairosvg

os.makedirs("images", exist_ok=True)

image_urls = [
    "https://cdn.simpleicons.org/nike",
    "https://cdn.simpleicons.org/apple",
    "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
    "https://cdn.simpleicons.org/samsung",
    "https://cdn.simpleicons.org/spotify",
    "https://cdn.simpleicons.org/netflix",
    "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
    "https://cdn.simpleicons.org/google",
    "https://cdn.simpleicons.org/tesla",
    "https://cdn.simpleicons.org/adidas",

    "https://cdn.simpleicons.org/adidas",
    "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
    "https://cdn.simpleicons.org/google",
    "https://cdn.simpleicons.org/apple",
    "https://cdn.simpleicons.org/netflix",
    "https://cdn.simpleicons.org/spotify",
    "https://cdn.simpleicons.org/google",
    "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
    "https://cdn.simpleicons.org/nike",
    "https://cdn.simpleicons.org/samsung",
    "https://cdn.simpleicons.org/tesla",
    "https://cdn.simpleicons.org/spotify",

    "https://randomuser.me/api/portraits/men/11.jpg",
    "https://randomuser.me/api/portraits/women/11.jpg",
    "https://randomuser.me/api/portraits/men/21.jpg",
    "https://randomuser.me/api/portraits/women/21.jpg",
    "https://randomuser.me/api/portraits/men/31.jpg",
    "https://randomuser.me/api/portraits/women/31.jpg",
    "https://randomuser.me/api/portraits/men/41.jpg",
    "https://randomuser.me/api/portraits/women/41.jpg"
]

for index, url in enumerate(image_urls):
    output_file = f"images/image{index+1}.png"

    try:
        response = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        if "svg" in content_type or url.lower().endswith(".svg"):
            png_data = cairosvg.svg2png(
                bytestring=response.content,
                output_width=512,
                output_height=512
            )

            with open(output_file, "wb") as f:
                f.write(png_data)
        else:
            image = Image.open(io.BytesIO(response.content))
            image = image.convert("RGBA")
            image.save(output_file, "PNG")

        print(f"[+] image{index+1}.png")

    except Exception as e:
        print(f"[-] image{index} failed: {e}")

print("\nDone.")
