# Contributing to LIFEFlow

Thank you for your interest in contributing to **LIFEFlow**! We welcome contributions from developers, clinical informaticians, and healthcare professionals.

---

## Code of Conduct
Please review and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) in all project interactions.

---

## Development Workflow

1. **Fork the Repository** and clone your fork locally:
   ```bash
   git clone https://github.com/phanindra267/Hemovigilance.git
   cd Hemovigilance
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run Migrations & Seed Demo Data**:
   ```bash
   python manage.py migrate
   python manage.py seed_demo_data
   ```

4. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/clinical-temperature-alerts
   ```

5. **Run the Test Suite**:
   Always ensure tests pass before committing:
   ```bash
   python manage.py check
   python manage.py test
   ```

6. **Submit a Pull Request**:
   Push your branch to GitHub and open a PR with a clear summary following the PR template.
