"""
Scheme Finder - Flask Web Application
A web-based interface for finding government schemes.
"""

from flask import Flask, render_template, request, jsonify, session
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scheme_loader import SchemeLoader
from src.eligibility_checker import EligibilityChecker
from src.models import UserProfile

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'scheme_finder_secret_key_2026'

# Load schemes on startup
loader = SchemeLoader('data/schemes_data.csv')
schemes = loader.load_schemes()
checker = EligibilityChecker(schemes)


@app.route('/')
def home():
    """Home page with introduction."""
    stats = checker.get_statistics()
    return render_template('index.html', stats=stats)


@app.route('/find-schemes')
def find_schemes():
    """Questionnaire page."""
    return render_template('questionnaire.html')


@app.route('/results', methods=['POST'])
def results():
    """Process form and show results."""
    # Get form data
    user_profile = UserProfile(
        state=request.form.get('state', 'Bihar'),
        age=int(request.form.get('age', 25)),
        gender=request.form.get('gender', 'Male'),
        category=request.form.get('category', 'General'),
        occupation=request.form.get('occupation', 'Other'),
        annual_income=float(request.form.get('income', 0)),
        is_bpl=request.form.get('bpl') == 'yes',
        has_disability=request.form.get('disability') == 'yes',
        marital_status=request.form.get('marital_status', 'Single'),
        district=request.form.get('district', 'Patna'),
        education_level=request.form.get('education', 'Graduate')
    )
    
    # Find eligible schemes
    eligible_schemes = checker.find_eligible_schemes(user_profile, min_score=35)
    
    return render_template('results.html', 
                         schemes=eligible_schemes, 
                         user=user_profile,
                         total_found=len(eligible_schemes))


@app.route('/scheme/<int:scheme_id>')
def scheme_detail(scheme_id):
    """Show detailed scheme information."""
    if 0 <= scheme_id < len(schemes):
        scheme = schemes[scheme_id]
        return render_template('scheme_detail.html', scheme=scheme, scheme_id=scheme_id)
    return "Scheme not found", 404


@app.route('/all-schemes')
def all_schemes():
    """Show all available schemes."""
    return render_template('all_schemes.html', schemes=schemes)


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@app.route('/api/schemes')
def api_schemes():
    """API endpoint to get all schemes as JSON."""
    scheme_list = []
    for i, scheme in enumerate(schemes):
        scheme_list.append({
            'id': i,
            'name': scheme.scheme_name,
            'state': scheme.state_name,
            'url': scheme.scheme_url
        })
    return jsonify(scheme_list)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  SCHEME FINDER WEB APPLICATION")
    print("="*60)
    print(f"  Loaded {len(schemes)} government schemes")
    print("  Open browser: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
