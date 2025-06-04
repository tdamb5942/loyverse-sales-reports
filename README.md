# Loyverse Sales Reports (WIP)

[![CI](https://github.com/tdamb5942/loyverse-sales-reports/actions/workflows/ci.yml/badge.svg)](https://github.com/tdamb5942/loyverse-sales-reports/actions/workflows/ci.yml)

This project is a **work in progress portfolio piece** built to demonstrate my data engineering skills by solving a real business problem using modern tools and best practices.

The goal is to ingest, process, and analyze sales data from the [Loyverse](https://www.loyverse.com/) API using Python and `pandas`, enabling better reporting and insight generation for a small business.

## 🔧 Project Purpose

The project has a real-world use case: helping a small business streamline and analyze their point-of-sale data. While it’s based on an actual business, the repository is designed to showcase general-purpose data engineering and software practices.

## ✅ Features

- OAuth integration with Loyverse API
- Paginated receipt data ingestion
- Output as pandas DataFrames
- Tests with `pytest` and mocking
- Security-conscious token management
- Extensible for monthly data refresh and reporting

## 🚀 Tech Stack

- Python 3.12
- `httpx` for API communication
- `pandas` for data handling
- `pytest` for testing
- `ruff` for linting
- `uv` for dependency management

## 🔜 Coming Soon

- Flattening and enriching data for reporting
- Visualization layer
- Dockerized local PostgreSQL (optional)

## 🙋‍♂️ About Me

I'm a data engineer passionate about solving practical problems with clean, testable code and modern tooling. This repo is one example of my work — check out the issues and commits for how I think and build.

---

## Project Purpose

This project was created to generate sales reports for Anahaw(https://instagram.com/anahawdauin) (my wife's business) using data from the Loyverse POS system.

...

*This project uses live data from [anahawdauin.com](https://www.anahawdauin.com), a yoga studio and plant-based restaurant & bar in the Philippines.*