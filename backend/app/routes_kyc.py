from flask import Blueprint, request, jsonify
from services.session_helper import require_session
from services.kyc_service import submit_kyc, get_kyc_status, review_kyc
from flask import g

kyc_bp = Blueprint('kyc', __name__)

@kyc_bp.route('/kyc/submit', methods=['POST'])
@require_session
def kyc_submit():
    user_id = request.user['user_id']
    documents = request.json.get('documents')
    if not documents:
        return jsonify({'error': 'Missing documents'}), 400
    sub = submit_kyc(user_id, documents)
    return jsonify({'message': 'KYC submitted', 'submission_id': sub.id}), 200

@kyc_bp.route('/kyc/status', methods=['GET'])
@require_session
def kyc_status():
    user_id = request.user['user_id']
    status, sub = get_kyc_status(user_id) # get_kyc_status returns (status_string, submission_object_or_None)
    
    if sub: # KYCSubmission object exists
        return jsonify(sub.to_dict()), 200
    else: # No submission found
        # The 'status' variable already contains the appropriate status string from the service
        # (e.g., 'not_started' or 'no_submission')
        return jsonify({'status': status, 'message': 'No KYC submission found.'}), 200

@kyc_bp.route('/kyc/review', methods=['POST'])
@require_session
def kyc_review():
    # Only allow admin
    if request.user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    data = request.json
    submission_id = data.get('submission_id')
    status = data.get('status')
    notes = data.get('notes')
    if not submission_id or status not in ('approved', 'rejected'):
        return jsonify({'error': 'Invalid request'}), 400
    ok = review_kyc(submission_id, status, notes)
    if not ok:
        return jsonify({'error': 'Submission not found'}), 404
    return jsonify({'message': f'KYC {status}'}), 200
