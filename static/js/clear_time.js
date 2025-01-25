function clearTime(button) {
    const timeInterval = button.closest('.time-interval');
    if (timeInterval) {
        const inputs = timeInterval.querySelectorAll('input[type="time"]');
        inputs.forEach(input => {
            input.value = "";
        });
    }
}