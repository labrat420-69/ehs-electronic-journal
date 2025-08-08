/**
 * Real-time clock functionality for EHS Electronic Journal
 * Updates the sidebar clock display every second in EST timezone
 */

let clockInterval = null;

/**
 * Initialize real-time clock
 */
function initializeClock() {
    updateClock();
    
    // Update clock every second
    clockInterval = setInterval(updateClock, 1000);
    
    // Update clock when page becomes visible (handles browser tab switching)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            updateClock();
        }
    });
}

/**
 * Update the clock display
 */
function updateClock() {
    const clockElement = document.getElementById('current-time');
    if (!clockElement) return;
    
    try {
        const now = new Date();
        const estTime = now.toLocaleString('en-US', {
            timeZone: 'America/New_York',
            month: '2-digit',
            day: '2-digit',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
        
        clockElement.textContent = estTime;
        
        // Update any other time displays on the page
        updatePageTimeDisplays();
        
    } catch (error) {
        console.error('Error updating clock:', error);
        clockElement.textContent = 'Time Error';
    }
}

/**
 * Update any time displays on the current page
 */
function updatePageTimeDisplays() {
    // Update elements with class 'live-time'
    document.querySelectorAll('.live-time').forEach(element => {
        const format = element.dataset.format || 'full';
        element.textContent = formatCurrentTime(format);
    });
    
    // Update relative time displays
    document.querySelectorAll('[data-timestamp]').forEach(element => {
        const timestamp = element.dataset.timestamp;
        if (timestamp) {
            element.textContent = getRelativeTime(new Date(timestamp));
        }
    });
}

/**
 * Format current time based on format type
 */
function formatCurrentTime(format) {
    const now = new Date();
    
    switch (format) {
        case 'date':
            return now.toLocaleDateString('en-US', {
                timeZone: 'America/New_York',
                month: '2-digit',
                day: '2-digit',
                year: 'numeric'
            });
        
        case 'time':
            return now.toLocaleTimeString('en-US', {
                timeZone: 'America/New_York',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        
        case 'datetime':
            return now.toLocaleString('en-US', {
                timeZone: 'America/New_York',
                month: '2-digit',
                day: '2-digit',
                year: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        
        case 'full':
        default:
            return now.toLocaleString('en-US', {
                timeZone: 'America/New_York',
                month: '2-digit',
                day: '2-digit',
                year: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            });
    }
}

/**
 * Get relative time (e.g., "2 minutes ago", "1 hour ago")
 */
function getRelativeTime(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSecs < 60) {
        return diffSecs <= 1 ? 'just now' : `${diffSecs} seconds ago`;
    } else if (diffMins < 60) {
        return diffMins === 1 ? '1 minute ago' : `${diffMins} minutes ago`;
    } else if (diffHours < 24) {
        return diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
    } else if (diffDays < 7) {
        return diffDays === 1 ? '1 day ago' : `${diffDays} days ago`;
    } else {
        // For older dates, show the actual date
        return date.toLocaleDateString('en-US', {
            timeZone: 'America/New_York',
            month: '2-digit',
            day: '2-digit',
            year: 'numeric'
        });
    }
}

/**
 * Get current EST timestamp for forms
 */
function getCurrentESTTimestamp() {
    const now = new Date();
    return now.toLocaleString('en-US', {
        timeZone: 'America/New_York',
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

/**
 * Auto-fill current timestamp in forms
 */
function autoFillCurrentTime() {
    // Auto-fill elements with class 'auto-timestamp'
    document.querySelectorAll('.auto-timestamp').forEach(element => {
        if (!element.value) {
            element.value = getCurrentESTTimestamp();
        }
    });
    
    // Auto-fill elements with class 'auto-date'
    document.querySelectorAll('.auto-date').forEach(element => {
        if (!element.value) {
            const now = new Date();
            element.value = now.toLocaleDateString('en-US', {
                timeZone: 'America/New_York',
                month: '2-digit',
                day: '2-digit',
                year: 'numeric'
            });
        }
    });
}

/**
 * Validate date input format (MM/DD/YYYY)
 */
function validateDateFormat(dateString) {
    const pattern = /^(0[1-9]|1[0-2])\/(0[1-9]|[12][0-9]|3[01])\/\d{4}$/;
    return pattern.test(dateString);
}

/**
 * Validate time input format (H:MM AM/PM)
 */
function validateTimeFormat(timeString) {
    const pattern = /^(1[0-2]|[1-9]):[0-5][0-9] (AM|PM)$/i;
    return pattern.test(timeString);
}

/**
 * Validate datetime input format (MM/DD/YYYY H:MM AM/PM)
 */
function validateDateTimeFormat(dateTimeString) {
    const pattern = /^(0[1-9]|1[0-2])\/(0[1-9]|[12][0-9]|3[01])\/\d{4} (1[0-2]|[1-9]):[0-5][0-9] (AM|PM)$/i;
    return pattern.test(dateTimeString);
}

/**
 * Convert EST date/time to UTC for server submission
 */
function convertESTToUTC(estDateTimeString) {
    try {
        // Parse the EST date/time string
        const estDate = new Date(estDateTimeString + ' EST');
        return estDate.toISOString();
    } catch (error) {
        console.error('Error converting EST to UTC:', error);
        return null;
    }
}

/**
 * Convert UTC date/time to EST for display
 */
function convertUTCToEST(utcDateTimeString) {
    try {
        const utcDate = new Date(utcDateTimeString);
        return utcDate.toLocaleString('en-US', {
            timeZone: 'America/New_York',
            month: '2-digit',
            day: '2-digit',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    } catch (error) {
        console.error('Error converting UTC to EST:', error);
        return utcDateTimeString;
    }
}

/**
 * Stop the clock interval (useful for cleanup)
 */
function stopClock() {
    if (clockInterval) {
        clearInterval(clockInterval);
        clockInterval = null;
    }
}

/**
 * Restart the clock interval
 */
function restartClock() {
    stopClock();
    initializeClock();
}

// Export clock utilities to global namespace
EHSJournal.utils.clock = {
    getCurrentESTTimestamp,
    autoFillCurrentTime,
    validateDateFormat,
    validateTimeFormat,
    validateDateTimeFormat,
    convertESTToUTC,
    convertUTCToEST,
    formatCurrentTime,
    getRelativeTime,
    stop: stopClock,
    restart: restartClock
};

// Auto-fill timestamps when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Small delay to ensure all elements are loaded
    setTimeout(autoFillCurrentTime, 100);
});

// Handle page visibility changes to keep clock accurate
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, we can reduce update frequency if needed
    } else {
        // Page is visible, ensure clock is accurate
        updateClock();
    }
});