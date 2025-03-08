import os
import datetime
import subprocess
import shutil
import zipfile

# Oracle credentials and settings
ORACLE_SID = "HOSPITAL"  # Replace with your Oracle SID
DB_USER = "EHOS"
DB_PASS = "EHOS"
SERVER_IP = "192.168.3.250"
BACKUP_DIR = "F:\\oracle_backups"  # Directory where backups will be stored

# Backup file name based on the day of the week
current_day = datetime.datetime.now().strftime("%A").upper()
backup_file = os.path.join(BACKUP_DIR, "{}_BK.dmp".format(current_day))

# Log file name based on the day of the week
log_file = os.path.join(BACKUP_DIR, "{}_BK_LOG.txt".format(current_day))

# Function to perform the Oracle backup using exp command
def perform_backup():
    # Ensure the backup directory exists
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # Clear and rewrite the log file
    with open(log_file, "w") as log:
        log.write("{}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        log.write("Starting backup for {}...\n".format(current_day))

    # Command to execute the Oracle export utility (exp) for the EHOS user schema
    command = "exp {}/{}@{}:{}/{} owner={} file={} ".format(
        DB_USER, DB_PASS, SERVER_IP, '1521', ORACLE_SID, DB_USER, backup_file
    )

    try:
        print("Starting backup for {}...".format(current_day))
        
        # Run the backup command and log output
        with open(log_file, "a") as log:
            result = subprocess.call(command, shell=True, stdout=log, stderr=subprocess.STDOUT)
            if result == 0:
                log.write("Backup completed: {}\n".format(backup_file))
                print("Backup completed: {}".format(backup_file))
                zip_backup()
            else:
                log.write("Backup failed with exit code: {}\n".format(result))
                print("Backup failed with exit code: {}".format(result))

    except Exception as e:
        print("Error during backup: {}".format(e))
        with open(log_file, "a") as log:
            log.write("Error during backup: {}\n".format(e))

# Function to zip the backup file
def zip_backup():
    zip_filename = backup_file.replace(".dmp", ".zip")
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_file, os.path.basename(backup_file))
        os.remove(backup_file)  # Delete the original .DMP file after zipping
        print("Backup compressed and saved as: {}".format(zip_filename))
        with open(log_file, "a") as log:
            log.write("Backup compressed and saved as: {}\n".format(zip_filename))
    except Exception as e:
        print("Error during zipping: {}".format(e))
        with open(log_file, "a") as log:
            log.write("Error during zipping: {}\n".format(e))

# Function to clean up old backups, keeping only 7 backup zip files
def cleanup_backups():
    files = [f for f in os.listdir(BACKUP_DIR) if f.endswith("_BK.zip")]
    files.sort()  # Sort files alphabetically by day (e.g., MONDAY_BK.zip)
    
    # Keep only the last 7 backups
    while len(files) > 7:
        old_backup = files.pop(0)  # Remove the oldest backup
        os.remove(os.path.join(BACKUP_DIR, old_backup))
        print("Deleted old backup: {}".format(old_backup))
        with open(log_file, "a") as log:
            log.write("Deleted old backup: {}\n".format(old_backup))

# Main function to run the backup and cleanup
def main():
    perform_backup()
    cleanup_backups()

# Run the script at 1:00 AM daily using Task Scheduler
if __name__ == "__main__":
    main()
