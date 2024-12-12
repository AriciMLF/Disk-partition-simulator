Project Description: 
The Disk Partition Simulator is a Python-based project that mimics the functionality of a disk partitioning system. It allows users to create and manage virtual disk partitions, navigate directories, and perform file operations using a Unix-like interface. The project provides a robust structure for interacting with a simulated disk, supporting file creation, editing, and retrieval while persisting data across sessions.

Features
Partition Management:

Create and manage virtual partitions with specified sizes.
Persistent metadata ensures partitions and files remain intact between sessions.
Unix-Like Navigation:

Access a specific partition and navigate directories using commands:
ls: List files and directories.
cd <directory>: Change directory.
mkdir <directory>: Create a new directory.
rmdir <directory>: Remove an empty directory.
touch <file>: Create a new file.
rm <file>: Delete a file.
edit <file> <new_content>: Modify the content of a text file.
cat <file>: Display the content of a text file.
File Operations:

Files can be created, edited, and deleted within directories.
The system maintains accurate metadata for file size and location.
Persistence:

All partition and file metadata are saved to disk, ensuring no data is lost when the program is restarted.

!Update! User Management:

Added user accounts for partitions to control access and permissions.
Support multi-user functionality with authentication.
Planned Features:
1.Encryption:

Implement encryption for files and directories to secure data stored in the virtual disk.
Enable decryption when accessing files with appropriate permissions.

Potential Use Cases
Educational Tool: Learn about file systems, directory structures, and partitioning in a simulated environment.
Programming Practice: Experiment with concepts like metadata management, file operations, and Unix-like commands.
Portfolio Project: Showcase skills in Python programming, file handling, and system simulation.
Future Directions
The project aims to evolve into a complete disk simulation system with:

File encryption to secure sensitive data.
Multi-user support for realistic partition management scenarios.
Enhanced error handling and logging for debugging and scalability.
This project is ideal for anyone interested in understanding low-level disk management concepts while building a functional and expandable Python application.
