# moonlight

# Installer les dépendances Node.js
cd web-app
npm install

# Copier les données dans public
# Windows
xcopy /E /I ..\data public\data
# Linux/Mac
cp -r ../data public/data

# Lancer en mode développement
npm run dev

# Accéder à http://localhost:3000

cd web-app
npm run build
# Les fichiers sont dans dist/
