# build.sh
set -o errexit

pip install -r requirements.txt

# Add this line to wipe the old static files cache
rm -rf staticfiles/

python manage.py collectstatic --no-input
python manage.py migrate