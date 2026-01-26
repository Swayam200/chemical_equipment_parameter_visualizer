#!/bin/bash

# This script sets up automatic virtual environment activation for backend and desktop-frontend folders

# Backup existing .zshrc
if [ -f ~/.zshrc ]; then
    cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)
    echo "✓ Backed up existing .zshrc"
fi

# Add auto-activation function to .zshrc
cat >> ~/.zshrc << 'EOF'

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

EOF

echo ""
echo "✓ Auto-activation function added to ~/.zshrc"
echo ""
echo "To activate the changes, run:"
echo "  source ~/.zshrc"
echo ""
echo "Or restart your terminal."
echo ""
echo "Now when you cd into backend/ or desktop-frontend/, the virtual environment will automatically:"
echo "  1. Create a venv if it doesn't exist"
echo "  2. Activate the venv"
echo "  3. Install requirements.txt if present"
echo ""
