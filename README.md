# Fintech-Fortress
Distributed Banking System with Zero Knowledge Proof
Fintech Fortress: A Distributed Banking System
Project Overview
Fintech Fortress is a secure and fault-tolerant distributed banking system designed to enhance modern financial services. It integrates Zero-Knowledge Proof (ZKP) authentication using the Schnorr Protocol, ensuring strong and private user authentication. The system also employs real-time database synchronization, database replication, and automated failover mechanisms to ensure continuous service availability and protection against data inconsistencies.

Key Features
Security & Authentication
Zero-Knowledge Proof (ZKP) Authentication using the Schnorr Protocol ensures secure authentication without revealing sensitive user credentials.
Database encryption protects stored information from unauthorized access.
Secure Sessions use HTTPS/TLS to prevent data interception.
Distributed System Architecture
Dual-Server Architecture with a primary and backup server to maintain high availability.
Automated Failover Mechanisms redirect traffic to the backup server during failures.
Database Replication & Synchronization ensure redundancy and fault tolerance.
Core Banking Features
Account Management (User profiles, account updates).
Secure Transactions (Deposits, Withdrawals, Transfers).
Transaction History with real-time logs.
Real-time Notifications for account activity.
Technologies Used
Backend: Python, Flask
Database: SQLite3 with replication and caching (Redis)
Security Protocols: Schnorr Protocol (ZKP), Data Encryption
Distributed Technologies: TCP/IP, Multi-threading
System Implementation
Web-based application with an administrator and client dashboard.
Load Balancer for distributing client requests efficiently.
Caching Mechanism to reduce database load and improve response time.
