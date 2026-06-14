const root = document.documentElement;
const savedTheme = localStorage.getItem("tn-theme");
if (savedTheme) root.dataset.theme = savedTheme;

document.getElementById("themeToggle")?.addEventListener("click", () => {
    root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem("tn-theme", root.dataset.theme);
});

const seatMap = document.getElementById("seatMap");
const selectedSeatsInput = document.getElementById("selectedSeats");
const passengerFields = document.getElementById("passengerFields");
const payButton = document.getElementById("payButton");
const fareTotal = document.getElementById("fareTotal");
const selectedSeatChips = document.getElementById("selectedSeatChips");
const selectedSeats = new Set();
const fareText = document.querySelector(".fare-line b")?.textContent || "0";
const farePerSeat = Number(fareText.replace(/[^0-9.]/g, "")) || 0;

function renderPassengerFields() {
    if (!passengerFields || !selectedSeatsInput || !payButton) return;
    const seats = Array.from(selectedSeats);
    selectedSeatsInput.value = seats.join(",");
    payButton.disabled = seats.length === 0;
    if (fareTotal) fareTotal.textContent = `INR ${(farePerSeat * seats.length).toFixed(2)}`;
    if (selectedSeatChips) {
        selectedSeatChips.innerHTML = seats.length
            ? seats.map((seat) => `<span class="seat-chip">Seat ${seat}</span>`).join("")
            : "<em>No seats selected</em>";
    }
    passengerFields.innerHTML = seats.map((seat) => `
        <div class="passenger-card">
            <strong>Seat ${seat}</strong>
            <input class="form-control mt-2" name="name_${seat}" placeholder="Passenger name" required>
            <div class="row g-2 mt-1">
                <div class="col"><input class="form-control" type="number" min="1" name="age_${seat}" placeholder="Age" required></div>
                <div class="col">
                    <select class="form-select" name="gender_${seat}">
                        <option>Male</option><option>Female</option><option>Other</option>
                    </select>
                </div>
            </div>
            <input class="form-control mt-2" name="phone_${seat}" placeholder="Phone">
        </div>
    `).join("");
}

seatMap?.addEventListener("click", (event) => {
    const button = event.target.closest(".seat");
    if (!button || button.disabled) return;
    const seat = button.dataset.seat;
    if (selectedSeats.has(seat)) {
        selectedSeats.delete(seat);
        button.classList.remove("selected");
    } else {
        selectedSeats.add(seat);
        button.classList.add("selected");
    }
    renderPassengerFields();
});

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add("is-visible");
    });
}, { threshold: 0.08 });

document.querySelectorAll(".route-card, .bus-result, .module-card, .metric-grid > div").forEach((node) => {
    observer.observe(node);
});
