# RoboRetail

**⚠️ WARNING: This is a deliberately vulnerable application for security testing purposes. DO NOT deploy in production environments.**

## Overview

RoboRetail is an intentionally vulnerable e-commerce platform for selling robots, designed to test AWS Security Agent's capabilities across design review, code review, and penetration testing.

## Purpose

This application contains 20+ security vulnerabilities across all OWASP Top 10 2025 categories with varying difficulty levels (easy, medium, hard, and chained exploits).

## Architecture

- **Frontend:** HTML/JavaScript web interface
- **Backend:** Python Flask REST API
- **Database:** PostgreSQL
- **Infrastructure:** AWS (VPC, EC2/ECS, RDS, ALB)
- **IaC:** AWS CDK (Python)

## Features

- User authentication and registration
- Robot product catalog with search
- Shopping cart and order processing
- Admin panel
- User profile with file upload
- Report export functionality

## Security Testing

This application is specifically designed to evaluate:
- Design review capabilities
- Code review and SAST detection
- Penetration testing effectiveness
- Vulnerability chaining detection

## Project Status

🚧 **In Development** - Phase 1: Setup & Planning Complete

## License

This project is for internal testing purposes only.
