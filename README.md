## Setup

1. Open command prompt navigate to project directory and run.

   ```shell
   python setup_script.py
   ```
2. Create a discord server for testing.
3. Create Discord Bot on [Discord Developer Portal](https://discord.com/developers/applications) copy its TOKEN and invite to your testing server.
   Refer to video below
   
   https://github.com/Super-EvilTeam/Thrax_bot/assets/99067991/e128e969-5587-4317-888d-b978e75adfee
4. Create `.env` file and add following lines.

   ```properties
   TOKEN = "add discord bot token here from previous step"
   FORM = "https://docs.google.com/forms/d/1JXLxeXnhAwWBADlC_yS9_IQY9gwb1Jg8RM79mAoLSVM/edit?usp=drivesdk"
   ```
5. Run `main.py` to start application.

## Docker

1. Make sure you are in the directory where your `Dockerfile` is located.
2. Open a terminal and run the following command to build the Docker image.

   ```shell
   docker build -t thrax_bot .
   ```

   This command will build the Docker image using the `Dockerfile` present in the current directory (`.`).
3. After the build completes, you can run your container with the following command:

   ```shell
   docker run -dp 3000:3000 thrax_bot
   ```

   This command will run the container, mapping port 3000 of the container to port 3000 of your host machine (adjust ports as necessary).
4. Your app should be available at http://localhost:3000 if your Discord bot exposes any services on that port.