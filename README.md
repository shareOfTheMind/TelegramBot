# MindVirus Telegram Bot

MindVirus is a Python-powered Telegram bot designed to foster a collaborative social media experience within a dedicated Telegram feed. Using the bot, users can share content from Instagram and other media types directly to the feed, creating a community-driven space for social media enthusiasts.

## Features

- **Instagram Integration**: Users can send Instagram URLs to the bot, which pulls the associated media using [Instaloader](https://github.com/instaloader/instaloader) and forwards it to the main feed, **MindVirus**.
- **Universal Media Support**: In addition to Instagram, users can send photos, videos, and text messages, all of which are forwarded to the feed.
- **Community-Driven**: The feed serves as a central hub for users who love sharing and discussing social media content.

## Future Features (In Development)
- **Mini-Feeds**: Group related content together into custom collections or mini-feeds, making it easier to browse and explore similar topics.
- **Contribution Tokens**: Earn tokens based on your contributions and interactions within the feed. The more you share and engage, the more tokens you'll earn, unlocking potential rewards and recognition.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/mindvirus-bot.git
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.8+ installed. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory to set up necessary environment variables:
   - `TELEGRAM_API_TOKEN`: Your Telegram bot API token.
   - `INSTAGRAM_USERNAME`: The Instagram account's username for Instaloader.
   - `INSTAGRAM_PASSWORD`: The associated password (ensure you have two-factor authentication disabled for smooth integration).

4. **Run the Bot**:
   Start the bot using the following command:
   ```bash
   python tgram_bot_runner.py
   ```

## Usage

1. **Sending Instagram URLs**: Users can send Instagram post URLs to the bot, and the media will be extracted and forwarded to the **MindVirus** feed.
2. **Forwarding Media**: The bot supports forwarding any media type (images, videos, and text) sent to it by users to the feed.
3. **Interactive Feed**: Engage with content shared by others and contribute to the growing collection of media on the MindVirus feed.

## Contributing

We welcome contributions! Feel free to open issues or submit pull requests for any bugs or new features you'd like to see. Please refer to the `CONTRIBUTING.md` for guidelines on contributing.

## License

This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details.

---

Let me know if you want any modifications!
