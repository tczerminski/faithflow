const indicator = document.getElementById("scroll-indicator");
const scrollArrow = document.getElementById("scroll-arrow");

function updateScrollIndicator() {
    const scrollable = document.documentElement;
    const scrollTop = scrollable.scrollTop;
    const scrollHeight = scrollable.scrollHeight;
    const clientHeight = scrollable.clientHeight;

    const scrolledToBottom = scrollTop + clientHeight >= scrollHeight - 20;

    if (indicator) {
        indicator.style.opacity = scrolledToBottom ? "0" : "1";
    }
}

document.addEventListener("scroll", updateScrollIndicator);
window.addEventListener("resize", updateScrollIndicator);
window.addEventListener("load", updateScrollIndicator);

if (scrollArrow) {
    scrollArrow.addEventListener("click", () => {
        window.scrollBy({
            top: window.innerHeight,
            behavior: "smooth"
        });
    });
}
