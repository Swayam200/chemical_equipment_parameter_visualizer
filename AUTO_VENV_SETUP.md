# Auto Virtual Environment Activation Setup

This setup automatically activates Python virtual environments when you navigate to the `backend/` or `desktop-frontend/` directories.

## Quick Setup

### Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
./setup_auto_venv.sh
```

Then reload your shell:

```bash
source ~/.zshrc
```

### Option 2: Manual Setup

Add this function to your `~/.zshrc` file:

```bash
# Auto-activate virtual environment when entering backend or desktop-frontend directories
autoload -U add-zsh-hook

auto_activate_venv() {
    # Check if we're in backend or desktop-frontend folder
    if [[ "$PWD" == */web_application_screening_task/backend* ]] || [[ "$PWD" == */web_application_screening_task/desktop-frontend* ]]; then
        # Find the project root (where backend and desktop-frontend are located)
        local project_root=""

        if [[ "$PWD" == */backend* ]]; then
            project_root="${PWD%/backend*}"
            local venv_path="$project_root/backend/venv"
        elif [[ "$PWD" == */desktop-frontend* ]]; then
            project_root="${PWD%/desktop-frontend*}"
            local venv_path="$project_root/desktop-frontend/venv"
        fi

        # Check if venv exists
        if [ -d "$venv_path" ]; then
            # Only activate if not already in a virtual environment or in a different one
            if [[ "$VIRTUAL_ENV" != "$venv_path" ]]; then
                source "$venv_path/bin/activate"
                echo "🐍 Activated virtual environment: $venv_path"
            fi
        else
            # Create venv if it doesn't exist
            echo "⚙️  Virtual environment not found. Creating one at $venv_path..."
            python3 -m venv "$venv_path"
            source "$venv_path/bin/activate"
            echo "✓ Created and activated virtual environment"

            # Install requirements if they exist
            local req_file=""
            if [[ "$PWD" == */backend* ]]; then
                req_file="$project_root/backend/requirements.txt"
            elif [[ "$PWD" == */desktop-frontend* ]]; then
                req_file="$project_root/desktop-frontend/requirements.txt"
            fi

            if [ -f "$req_file" ]; then
                echo "📦 Installing dependencies from requirements.txt..."
                pip install -r "$req_file"
            fi
        fi
    else
        # Deactivate if we leave the project directories
        if [[ -n "$VIRTUAL_ENV" ]] && [[ "$VIRTUAL_ENV" == */web_application_screening_task/* ]]; then
            deactivate 2>/dev/null
            echo "👋 Deactivated virtual environment"
        fi
    fi
}

add-zsh-hook chpwd auto_activate_venv

# Also run on shell startup if we're already in a project directory
auto_activate_venv
```

Then reload your shell:

```bash
source ~/.zshrc
```

## How It Works

1. **Automatic Activation**: When you `cd` into `backend/` or `desktop-frontend/`, the virtual environment automatically activates
2. **Automatic Creation**: If the venv doesn't exist, it will be created automatically
3. **Dependency Installation**: If `requirements.txt` exists, dependencies are installed automatically
4. **Automatic Deactivation**: When you leave the project directories, the venv is deactivated

## Usage Example

```bash
# Navigate to backend - venv activates automatically
cd ~/Desktop/fossee/web_application_screening_task/backend
# 🐍 Activated virtual environment: /Users/Swayam/Desktop/fossee/web_application_screening_task/backend/venv

# Your venv is now active - run Django commands
python manage.py runserver

# Navigate out - venv deactivates automatically
cd ..
# 👋 Deactivated virtual environment

# Navigate to desktop-frontend - its venv activates
cd desktop-frontend
# 🐍 Activated virtual environment: /Users/Swayam/Desktop/fossee/web_application_screening_task/desktop-frontend/venv

# Run the desktop app
python main.py
```

## Benefits

✅ No need to manually run `source venv/bin/activate`  
✅ Automatically creates venv if missing  
✅ Installs dependencies from requirements.txt  
✅ Separate virtual environments for backend and desktop-frontend  
✅ Clean automatic deactivation when leaving directories

## Troubleshooting

**Issue**: Function not working after setup  
**Solution**: Make sure you ran `source ~/.zshrc` or restart your terminal

**Issue**: Getting errors about python3 not found  
**Solution**: Install Python 3 or adjust the `python3` command in the function

**Issue**: Want to disable auto-activation temporarily  
**Solution**: Comment out the `add-zsh-hook chpwd auto_activate_venv` line in your ~/.zshrc

## Rollback

If you want to remove auto-activation, your original `.zshrc` was backed up to:

```
~/.zshrc.backup.[timestamp]
```

You can restore it with:

```bash
cp ~/.zshrc.backup.[timestamp] ~/.zshrc
source ~/.zshrc
```
