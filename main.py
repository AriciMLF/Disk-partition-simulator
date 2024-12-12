import os
import pickle

class VirtualDisk:
    def __init__(self, size):
        self.size = size  # Disk size in bytes
        self.disk_file = "virtual_disk.bin"
        self.metadata_file = "metadata.pkl"
        self.users_file = "users.pkl"
        self.partitions = {}  # {partition_name: (start_offset, size)}
        self.file_allocation_table = {}  # {partition_name: directory tree}
        self.partion_users = {} # {partion name: (user, password)}

        # Load metadata if available
        self.load_metadata()
        self.load_users()

        # Initialize the virtual disk file
        if not os.path.exists(self.disk_file):
            with open(self.disk_file, "wb") as f:
                f.write(b"\x00" * self.size)

    def save_users(self):
        with open(self.users_file, "wb") as f:
            pickle.dump(self.partion_users, f)
    
    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, "rb") as f:
                self.partion_users = pickle.load(f)
        else:
            self.partion_users = {}


    def save_metadata(self):
        """Save partitions and file allocation table to disk."""
        with open(self.metadata_file, "wb") as f:
            pickle.dump((self.partitions, self.file_allocation_table), f)

    def load_metadata(self):
        """Load partitions and file allocation table from disk if available."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "rb") as f:
                self.partitions, self.file_allocation_table = pickle.load(f)
        else:
            self.partitions = {}
            self.file_allocation_table = {}

    def create_partition(self, name, size):
        """Create a new partition."""
        if name in self.partitions:
            return f"Partition '{name}' already exists."

        # Calculate available space
        used_space = sum(p[1] for p in self.partitions.values())
        available_space = self.size - used_space

        if size > available_space:
            return "Not enough space to create the partition."

        # Determine the starting offset
        start = max((p[0] + p[1] for p in self.partitions.values()), default=0)
        self.partitions[name] = (start, size)
        self.file_allocation_table[name] = {"/": {}}  # Initialize root directory
        self.save_metadata()
        return f"Partition '{name}' created with size {size} bytes."

    def navigate_partition(self, partition_name):
        """Provide a Unix-like interface for navigating and managing the partition."""
        if partition_name not in self.partitions:
            print(f"Error: Partition '{partition_name}' does not exist.")
            return

        while True:
            print("1. Log into this partion")
            print("2. Create user for this partition")
            print("3. Exit")
            choice = input("Choose your action: ")
            if choice == "1":
                if self.log_in_user(partition_name)[0]:
                    print("Successfully logged in")
                    break
                else: print("Wrong username or password")
            elif choice == "2":
                if self.create_user(partition_name):
                    print("User created succesfully")
                    break
                else: print("Too many users")
        
            elif choice == "3":
                print("Exiting...")
                return
            else:
                print("Invalid choice. Please try again.")


        print(f"Entering partition '{partition_name}'...")
        current_dir = self.file_allocation_table[partition_name]["/"]
        path = "/"

        while True:
            command = input(f"{partition_name}:{path} $ ").strip().split()
            if not command:
                continue

            cmd = command[0]
            args = command[1:]

            if cmd == "ls":
                print(" ".join(current_dir.keys()))

            elif cmd == "cd":
                if not args:
                    print("Error: No directory specified.")
                elif args[0] == "..":
                    if path != "/":
                        path = "/".join(path.strip("/").split("/")[:-1])
                        current_dir = self.file_allocation_table[partition_name]["/"]
                        for subdir in path.strip("/").split("/"):
                            if subdir:
                                current_dir = current_dir[subdir]
                elif args[0] in current_dir and isinstance(current_dir[args[0]], dict):
                    path = f"{path.rstrip('/')}/{args[0]}".replace("//", "/")
                    current_dir = current_dir[args[0]]
                else:
                    print(f"Error: Directory '{args[0]}' does not exist.")

            elif cmd == "mkdir":
                if not args:
                    print("Error: No directory name specified.")
                elif args[0] in current_dir:
                    print(f"Error: Directory '{args[0]}' already exists.")
                else:
                    current_dir[args[0]] = {}
                    self.save_metadata()

            elif cmd == "touch":
                if not args:
                    print("Error: No file name specified.")
                elif args[0] in current_dir:
                    print(f"Error: File '{args[0]}' already exists.")
                else:
                    # Initialize the file with zero size and allocate space
                    partition_start, partition_size = self.partitions[partition_name]
                    used_space = sum(f[1] for f in current_dir.values() if isinstance(f, tuple))
                    available_space = partition_size - used_space

                    if available_space <= 0:
                        print("Error: Not enough space to create the file.")
                    else:
                        # Set initial metadata for the file
                        current_dir[args[0]] = (partition_start + used_space, 0)  # Offset and size
                        self.save_metadata()
                        print(f"File '{args[0]}' created.")


            elif cmd == "rm":
                if not args:
                    print("Error: No file name specified.")
                elif args[0] not in current_dir:
                    print(f"Error: File '{args[0]}' does not exist.")
                elif isinstance(current_dir[args[0]], dict):
                    print(f"Error: '{args[0]}' is a directory. Use 'rmdir' to remove directories.")
                else:
                    del current_dir[args[0]]
                    self.save_metadata()

            elif cmd == "rmdir":
                if not args:
                    print("Error: No directory name specified.")
                elif args[0] not in current_dir or not isinstance(current_dir[args[0]], dict):
                    print(f"Error: Directory '{args[0]}' does not exist.")
                elif current_dir[args[0]]:
                    print(f"Error: Directory '{args[0]}' is not empty.")
                else:
                    del current_dir[args[0]]
                    self.save_metadata()

            elif cmd == "edit":
                if len(args) < 2:
                    print("Usage: edit <file> <new_content>")
                else:
                    filename = args[0]
                    new_content = " ".join(args[1:])  # Combine the rest of the arguments as content
                    result = self.edit_file(partition_name, path, filename, new_content)
                    print(result)

            elif cmd == "cat":
                if not args:
                    print("Usage: cat <file>")
                else:
                    filename = args[0]
                    result = self.read_file(partition_name, path, filename)
                    print(result)

            elif cmd == "exit":
                print(f"Exiting partition '{partition_name}'...")
                break

            else:
                print(f"Error: Command '{cmd}' not recognized.")

    def edit_file(self, partition_name, path, filename, new_content):
        """Edit the content of a text file in the specified directory."""
        if partition_name not in self.partitions:
            return f"Error: Partition '{partition_name}' does not exist."

        # Navigate to the specified directory
        current_dir = self.file_allocation_table[partition_name]["/"]
        for subdir in path.strip("/").split("/"):
            if subdir:
                if subdir in current_dir and isinstance(current_dir[subdir], dict):
                    current_dir = current_dir[subdir]
                else:
                    return f"Error: Path '{path}' does not exist."

        # Check if the file exists
        if filename not in current_dir or not isinstance(current_dir[filename], tuple):
            return f"Error: File '{filename}' does not exist in path '{path}'."

        # Retrieve file metadata
        file_offset, file_size = current_dir[filename]

        # Calculate available space
        partition_start, partition_size = self.partitions[partition_name]
        used_space = sum(f[1] for f in current_dir.values() if isinstance(f, tuple))
        available_space = partition_size - used_space + file_size  # Include the current file size

        new_content_bytes = new_content.encode()
        if len(new_content_bytes) > available_space:
            return "Not enough space to update the file with the new content."

        # Write the new content to the virtual disk
        with open(self.disk_file, "r+b") as f:
            f.seek(file_offset)
            f.write(new_content_bytes)
            f.truncate(file_offset + len(new_content_bytes))  # Ensure old content beyond new size is removed

        # Update the file size in the directory
        current_dir[filename] = (file_offset, len(new_content_bytes))
        self.save_metadata()
        return f"File '{filename}' updated successfully."


    def read_file(self, partition_name, path, filename):
        """Read the content of a text file."""
        if partition_name not in self.partitions:
            return f"Error: Partition '{partition_name}' does not exist."

        # Navigate to the specified directory
        current_dir = self.file_allocation_table[partition_name]["/"]
        for subdir in path.strip("/").split("/"):
            if subdir:
                if subdir in current_dir and isinstance(current_dir[subdir], dict):
                    current_dir = current_dir[subdir]
                else:
                    return f"Error: Path '{path}' does not exist."

        # Check if the file exists
        if filename not in current_dir or not isinstance(current_dir[filename], tuple):
            return f"Error: File '{filename}' does not exist in path '{path}'."

        # Retrieve file metadata
        file_offset, file_size = current_dir[filename]

        # Read the file content from the virtual disk
        with open(self.disk_file, "rb") as f:
            f.seek(file_offset)
            content = f.read(file_size)

        return content.decode()
    
    def create_user(self, partion_name):
        if partion_name in self.partion_users:
            return False
        username = input("Enter username: ")
        password = input("Create password: ")
        self.partion_users[partion_name] = (username, password)
        self.save_users()
        return True
    
    def log_in_user(self, partion_name):
        username = input("Enter username: ")
        password = input("Enter password: ")
        if username != self.partion_users[partion_name][0] and password != self.partion_users[partion_name][1]:
            return False, "Wrong user or password"
        return True, f"User {username} logged in successfully"

# Main Program
def main():
    disk = VirtualDisk(1024 * 1024)  # 1 MB Disk

    while True:
        print("\nDisk Partition Simulator")
        print("1. Create Partition")
        print("2. Choose Partition")
        print("3. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            name = input("Enter partition name: ")
            size = int(input("Enter partition size (bytes): "))
            print(disk.create_partition(name, size))
        elif choice == "2":
            name = input("Enter partition name to access: ")
            disk.navigate_partition(name)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
