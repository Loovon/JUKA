let index = 5;
const slides = document.querySelector(".slide");
const totalSlides = slides.children.length;

setInterval(() => {
    index = (index + 1) % totalSlides;
    slides.style.transform = `translateX(-${index * 100}%)`;
    slides.style.transition = "transform 0.5s ease-in-out";
}, 3000);
