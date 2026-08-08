"""
Synthetic development dataset for the Google Play Review Classification Platform.

THIS IS NOT A REAL GOOGLE PLAY DATASET.
It is a small sample created strictly for local development, training smoke-tests,
and demonstration when a real dataset is not present.
"""

from __future__ import annotations

import csv
from pathlib import Path

# (rating, review)
SAMPLES: list[tuple[int, str]] = [
    # Crash
    (1, "The app crashes every time I open it after the latest update."),
    (1, "Constant crashing on startup. Force close again and again."),
    (2, "App keeps crashing when I try to open messages."),
    (1, "It crashed three times today. Unusable."),
    (2, "Force close happens whenever I upload a photo."),
    (1, "Crashes randomly during checkout. Please fix."),
    (2, "After update the app is crashing nonstop."),
    (1, "My phone says app stopped working. Crashes immediately."),
    (2, "Keeps closing when I switch tabs. Crash issue."),
    (1, "Worst update ever. Crashes on launch every single time."),
    # Login Problem
    (1, "I cannot login to my account."),
    (2, "Can't sign in even with correct password."),
    (1, "Login fails every time. Authentication error."),
    (2, "Unable to log in after changing my password."),
    (1, "Sign in page is broken. OTP never arrives."),
    (2, "Can't log in on my new phone."),
    (3, "Login sometimes works, sometimes not."),
    (1, "Cannot sign in to my account since yesterday."),
    (2, "Password reset works but then login fails."),
    (1, "Unable to login. Keeps saying invalid credentials."),
    # Performance Issue
    (2, "The app is so slow and laggy it freezes constantly."),
    (1, "Freezing every few minutes. Terrible performance."),
    (2, "Very slow loading. Takes forever to open."),
    (3, "A bit laggy when scrolling through the feed."),
    (1, "Not responding half the time. Hang issues."),
    (2, "Battery drain and lag after the last update."),
    (2, "Stuttering and freeze when opening camera."),
    (1, "App hangs on splash screen forever."),
    (3, "Sometimes slow but acceptable."),
    (2, "Laggy interface and freezing videos."),
    # UI Problem
    (2, "The interface is confusing and the layout is messy."),
    (3, "Buttons are too small and hard to tap."),
    (2, "Ugly design. The UI looks outdated."),
    (3, "Dark mode broken and font size is unreadable."),
    (2, "Hard to navigate. Cluttered screen layout."),
    (4, "Nice features but the button placement is awkward."),
    (2, "Confusing UI makes simple tasks difficult."),
    (3, "Interface needs a redesign. Layout overlaps."),
    (2, "The design of the home screen is cluttered."),
    (3, "UI problem with overlapping text on settings."),
    # Feature Request
    (4, "Please add dark mode support. Would like this feature."),
    (5, "Wish there was an offline mode. Feature request!"),
    (4, "It would be nice if you could add export to PDF."),
    (3, "Hope you add multi-language support soon."),
    (4, "Can you add a widget for the home screen?"),
    (5, "Would like a tablet layout. Please add it."),
    (4, "Should add fingerprint unlock. Missing feature."),
    (3, "Wish you had calendar sync."),
    (4, "Please add the ability to schedule posts."),
    (5, "Feature request: night mode and custom themes."),
    # Ads Complaint
    (1, "Too many ads. Advertisement every few seconds."),
    (2, "Full of ads and pop-up ads. Unusable."),
    (1, "Annoying ads everywhere. Forced ads before every action."),
    (2, "Ads are out of control after the update."),
    (1, "Too many advertisements. I can't even use the app."),
    (2, "Popup ads cover the whole screen."),
    (1, "Worst ads experience. Constant advertisement spam."),
    (3, "Ads are okay but a bit too frequent."),
    (2, "Forced ads make watching content impossible."),
    (1, "Ad pop ups every minute. Terrible."),
    # Security Concern
    (1, "Worried about privacy. Feels unsafe with my personal data."),
    (2, "Security concern after reading about a data breach."),
    (1, "Think my account got hacked. Very unsafe."),
    (2, "Asks for too many permissions. Privacy issue."),
    (1, "Malware warning on install. Security problem."),
    (2, "Suspicious about how they handle personal data."),
    (1, "Hacker risk. No two-factor security options."),
    (3, "Privacy policy is unclear and concerning."),
    (2, "Unsafe payment page. Security looks weak."),
    (1, "Stolen account rumors. Privacy and security worries."),
    # Payment Problem
    (1, "Payment failed twice and I was still charged."),
    (2, "Refund not processed. Transaction stuck."),
    (1, "UPI payment failed but money was deducted."),
    (2, "Double charged for subscription. Billing error."),
    (1, "In-app purchase failed. Payment problem."),
    (2, "Cannot complete transaction. Money issues."),
    (1, "Subscription charged without consent. Refund please."),
    (3, "Payment sometimes fails on checkout."),
    (2, "Billing page errors when paying with card."),
    (1, "Purchase failed and support ignores refund requests."),
    # General Praise
    (5, "Excellent application. I love it."),
    (5, "Amazing app! Best app I have ever used."),
    (4, "Great experience overall. Highly recommend."),
    (5, "Love this app. Fantastic and wonderful."),
    (5, "Perfect! Awesome features and so good."),
    (4, "Very good app. Great for daily use."),
    (5, "Best app in this category. Excellent work."),
    (4, "Amazing update. Love it even more now."),
    (5, "Wonderful app. Highly recommend to friends."),
    (4, "Great and easy to use. Fantastic job."),
    # Other / mixed
    (3, "It is okay. Nothing special to mention."),
    (3, "Average app for basic needs."),
    (2, "Not what I expected from the description."),
    (4, "Works fine for my simple use case."),
    (3, "Decent but could be better."),
    (2, "Uninstalled after a week. Not useful for me."),
    (4, "Does the job. No major complaints."),
    (3, "It's fine. Using it occasionally."),
    (1, "Waste of time. Completely useless to me."),
    (5, "Solid tool for everyday tasks."),
    # Extra sentiment variety
    (5, "I love this product so much. Excellent quality."),
    (1, "Horrible experience. Do not download."),
    (4, "Pretty good overall after recent fixes."),
    (2, "Disappointed with customer support responses."),
    (3, "Neither good nor bad. Just average."),
    (5, "Absolutely amazing. Best decision to install."),
    (1, "Broken and frustrating beyond words."),
    (4, "Good enough for what I need."),
    (2, "Keeps showing errors for no reason."),
    (5, "Superb. Love this and recommend everyone."),
]


def main() -> None:
    out = Path(__file__).resolve().parent / "sample_reviews.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["Rating", "Review"])
        writer.writeheader()
        for rating, review in SAMPLES:
            writer.writerow({"Rating": rating, "Review": review})
    print(f"Wrote {len(SAMPLES)} sample reviews to {out}")
    print("NOTE: This is a synthetic sample dataset for development only.")


if __name__ == "__main__":
    main()
