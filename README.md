# SkilledGuild

**Problem Statement:**
People want to grow their abilities, connect with like-minded individuals, and collaborate on real-world projects. But most platforms silo learning, community, and teamwork into separate experiences. Meanwhile, sponsors and event organizers struggle to find the right partners and visibility. There’s no unified space where learners, teams, and opportunities naturally converge.

SkilledGuild fills this gap—bringing together growth, collaboration, and connection under one cohesive ecosystem.

## Description
SkilledGuild is a web-based platform that unifies learning, collaboration, and community-building under one roof. It helps individuals connect based on shared interests, build teams for hackathons or personal projects, and grow through practical, challenge-based learning. Unlike fragmented platforms that separate education from networking, SkilledGuild offers a seamless space to discover like-minded peers, showcase progress, and engage in meaningful collaboration.

Additionally, it bridges the gap between event organisers and sponsors, allowing both to find aligned opportunities through targeted discovery tools. Whether you're a learner, a builder, or a facilitator, SkilledGuild is where communities grow, ideas take shape, and real-world projects come to life.

## Features

- **User Registration & Authentication**
  - Secure sign-up, login, and profile management.
- **Guilds (Communities)**
  - Create, join, and explore Guilds based on interests or skills.
  - Forum-like discussions and posts within each Guild.
  - Guild dashboards and member management.
- **TeamUp Collaboration**
  - Set up a collaboration profile with skills, interests, and location.
  - Discover and connect with potential teammates for projects or hackathons.
  - Form or join teams, manage invitations, and collaborate efficiently.
- **User Profiles**
  - Rich profiles with bios, skills, interests, location, and social links.
  - Availability status for collaboration.
- **Dynamic Posts & Discussions**
  - Create, comment, and engage in threaded discussions within Guilds.
  - Tag posts and share resources.
- **Responsive & Modern UI**
  - Consistent, accessible design using Tailwind CSS and custom theming.

## Technologies Used

- **Backend:** Django (Python)
- **Frontend:** Tailwind CSS, JavaScript
- **Database:** SQLite (default, easily switchable to PostgreSQL/MySQL)

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/SkilledGuild.git
cd SkilledGuild
```

### 2. Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations
```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional, for admin access)
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser to start using SkilledGuild.

## Contribution Guidelines

- Fork the repository and create your feature branch (`git checkout -b feature/YourFeature`)
- Commit your changes with clear messages
- Push to your fork and submit a pull request
- Follow PEP8 and Django best practices
- Ensure all new features are covered by tests where possible

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact & Credits

- Developed by the SkilledGuild Team
- For questions, suggestions, or contributions, open an issue or contact the maintainers via GitHub.

Special thanks to all contributors and the open-source community!
