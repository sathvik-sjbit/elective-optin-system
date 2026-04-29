/**
 * ajax_seats.js
 * Real-time seat availability polling for ElectiveHub.
 *
 * CO5: AJAX Integration
 * Uses the Fetch API to poll the DRF /api/seats/ endpoint
 * and update seat counts in the catalog without page reload.
 */

/**
 * Refresh seat info for ALL courses on the current page.
 * Updates the seat bar width, color, and text dynamically.
 */
async function refreshAllSeats() {
    try {
        const response = await fetch('/api/seats/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
            }
        });

        if (!response.ok) return;
        const courses = await response.json();

        courses.forEach(course => {
            updateSeatDisplay(course);
        });

    } catch (error) {
        console.warn('Seat refresh failed:', error);
    }
}

/**
 * Update a single course's seat display in the catalog.
 * @param {Object} course - Serialized course data from API
 */
function updateSeatDisplay(course) {
    const textEl = document.getElementById(`seat-text-${course.id}`);
    const barEl = document.getElementById(`seat-bar-${course.id}`);

    if (!textEl && !barEl) return;

    const pct = Math.round((course.available_seats / course.total_seats) * 100);
    const colorClass = course.is_full ? 'bg-danger' :
                       pct <= 20 ? 'bg-danger' :
                       pct <= 50 ? 'bg-warning' : 'bg-success';
    const textColorClass = course.is_full ? 'text-danger' :
                           pct <= 20 ? 'text-danger' :
                           pct <= 50 ? 'text-warning' : 'text-success';

    // Update text badge
    if (textEl) {
        if (course.is_full) {
            textEl.innerHTML = '<span class="text-danger fw-semibold"><i class="bi bi-x-circle me-1"></i>Full</span>';
        } else {
            textEl.innerHTML = `<span class="${textColorClass} fw-semibold">${course.available_seats}/${course.total_seats}</span>`;
        }
    }

    // Update progress bar
    if (barEl) {
        barEl.style.width = `${pct}%`;
        barEl.className = `seat-bar-fill ${colorClass}`;
    }
}

/**
 * Fetch seat info for a specific course (used on submit form).
 * @param {string|number} courseId - Course primary key
 * @returns {Promise<Object>} Course seat data
 */
async function fetchSeatInfo(courseId) {
    const response = await fetch(`/api/seats/${courseId}/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
        }
    });
    if (!response.ok) throw new Error('Failed to fetch seat info');
    return response.json();
}

// Auto-start polling if we're on the catalog page (has course grid)
document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('courseGrid')) {
        // Initial refresh after 2s, then every 15s
        setTimeout(refreshAllSeats, 2000);
        setInterval(refreshAllSeats, 15000);
    }
});
