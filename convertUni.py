import json
import os


# ============================================================
# SETTINGS
# ============================================================

DATASET_FOLDER = input(
    "Enter the folder containing your JSON datasets: "
).strip()

OUTPUT_FILE = os.path.join(
    "preprossed_datasets",
    "universal_platform_dataset.json" if DATASET_FOLDER.startswith("platform") else "universal_company_dataset.json"
)


# ============================================================
# BASIC HELPERS
# ============================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def first_value(data, *keys, default=None):
    """Return the first existing, non-None value."""
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return default


def detect_platform(filename):
    name = filename.lower()

    if "instagram" in name:
        return "instagram"

    if "facebook" in name:
        return "facebook"

    if name.startswith("x") or "twitter" in name:
        return "x"

    if "google" in name or "play" in name:
        return "google_play"

    if "apple" in name or "app_store" in name:
        return "apple_app_store"

    return None


# ============================================================
# SOCIAL MEDIA NORMALIZER
# ============================================================

def normalize_social(platform, item):

    # X has its actual object inside "data"
    if platform == "x" and "data" in item:
        item = item["data"]

    metrics = item.get("public_metrics", {})

    profile = {
        "entity_type": "social_profile",

        "platform": platform,

        # Identity
        "id": first_value(
            item,
            "id"
        ),

        "username": first_value(
            item,
            "username"
        ),

        "display_name": first_value(
            item,
            "name",
            "display_name"
        ),

        # Description / bio
        "description": first_value(
            item,
            "biography",
            "about",
            "description"
        ),

        # Media
        "image_url": first_value(
            item,
            "profile_picture_url",
            "profile_image_url"
        ),

        # Website
        "website": first_value(
            item,
            "website"
        ),

        # Statistics
        "followers_count": first_value(
            item,
            "followers_count",
            default=metrics.get("followers_count", 0)
        ),

        "following_count": first_value(
            item,
            "following_count",
            default=metrics.get("following_count", 0)
        ),

        "posts_count": first_value(
            item,
            "posts_count",
            default=metrics.get(
                "posts_count",
                metrics.get("tweet_count", 0)
            )
        ),

        # Verification
        "verified": first_value(
            item,
            "verified",
            default=False
        ),

        # Account information
        "created_at": first_value(
            item,
            "created_at"
        ),

        "protected": first_value(
            item,
            "protected",
            default=False
        )
    }

    return profile


# ============================================================
# APP NORMALIZER
# ============================================================

def normalize_app(platform, item):

    # Apple uses JSON:API format
    if platform == "apple_app_store":

        data = item.get("data", {})
        attributes = data.get("attributes", {})

        app_id = data.get("id")

        name = first_value(
            attributes,
            "name"
        )

        package_id = first_value(
            attributes,
            "bundleId"
        )

        sku = first_value(
            attributes,
            "sku"
        )

        description = first_value(
            attributes,
            "description"
        )

        locale = first_value(
            attributes,
            "primaryLocale"
        )

        downloads = first_value(
            attributes,
            "downloads",
            default=0
        )

        return {
            "entity_type": "application",

            "platform": platform,

            # Universal ID
            "id": app_id,

            # App identity
            "name": name,

            "package_id": package_id,

            "sku": sku,

            # Description
            "description": description,

            # Developer
            "developer": None,

            # Media
            "image_url": None,

            # Statistics
            "downloads_count": downloads,

            # Classification
            "category": None,

            # Website
            "website": None,

            # Locale
            "locale": locale
        }


    # Google Play
    if platform == "google_play":

        package_name = first_value(
            item,
            "packageName"
        )

        name = first_value(
            item,
            "title",
            "name"
        )

        developer = first_value(
            item,
            "developer"
        )

        description = first_value(
            item,
            "description"
        )

        image = first_value(
            item,
            "icon",
            "image_url"
        )

        downloads = first_value(
            item,
            "downloads",
            "downloads_count",
            default=0
        )

        category = first_value(
            item,
            "category"
        )

        website = first_value(
            item,
            "developerWebsite",
            "website"
        )

        developer_email = first_value(
            item,
            "developerEmail"
        )

        privacy_policy = first_value(
            item,
            "privacyPolicy"
        )

        return {
            "entity_type": "application",

            "platform": platform,

            # Universal ID
            "id": package_name,

            # App identity
            "name": name,

            "package_id": package_name,

            "sku": None,

            # Description
            "description": description,

            # Developer
            "developer": developer,

            "developer_email": developer_email,

            # Media
            "image_url": image,

            # Statistics
            "downloads_count": downloads,

            # Classification
            "category": category,

            # Website
            "website": website,

            # Other useful information
            "privacy_policy": privacy_policy,

            "locale": None
        }


# ============================================================
# PROCESS FILE
# ============================================================

def process_file(path):

    filename = os.path.basename(path)

    platform = detect_platform(filename)

    if platform is None:
        print(f"⚠️ Unknown platform: {filename}")
        return []

    print(f"Processing {filename} → {platform}")

    data = load_json(path)

    if not isinstance(data, list):
        data = [data]

    results = []

    for item in data:

        if platform in {
            "instagram",
            "facebook",
            "x"
        }:

            results.append(
                normalize_social(
                    platform,
                    item
                )
            )

        elif platform in {
            "google_play",
            "apple_app_store"
        }:

            results.append(
                normalize_app(
                    platform,
                    item
                )
            )

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    if not os.path.isdir(DATASET_FOLDER):

        print("❌ Folder does not exist.")
        return

    files = [
        os.path.join(
            DATASET_FOLDER,
            filename
        )
        for filename in os.listdir(DATASET_FOLDER)
        if filename.lower().endswith(".json")
        and filename != "universal_dataset.json"
    ]

    if not files:

        print("❌ No JSON datasets found.")
        return

    universal_dataset = []

    print("\n====================================")
    print(" Digital Risk Protection Normalizer")
    print("====================================\n")

    for file in files:

        records = process_file(file)

        universal_dataset.extend(records)

        print(
            f"   → {len(records)} records\n"
        )

    # Save
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            universal_dataset,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("====================================")
    print("DONE ✅")
    print("====================================")
    print(
        f"Total records: {len(universal_dataset)}"
    )
    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
