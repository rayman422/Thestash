document.addEventListener('mousemove', (e) => {
	const cards = document.querySelectorAll('.blog-card');
	const mouseX = e.clientX;
	const mouseY = e.clientY;
	cards.forEach(card => {
		const rect = card.getBoundingClientRect();
		const cardCenterX = rect.left + rect.width / 2;
		const cardCenterY = rect.top + rect.height / 2;
		const deltaX = (mouseX - cardCenterX) / rect.width;
		const deltaY = (mouseY - cardCenterY) / rect.height;
		const rotateX = deltaY * 5;
		const rotateY = deltaX * 5;
		card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
	});
});

const logo = document.querySelector('.logo');
if (logo) {
	setInterval(() => {
		if (Math.random() < 0.1) {
			logo.style.textShadow = '2px 0 #ff00ff, -2px 0 #00ff41';
			setTimeout(() => {
				logo.style.textShadow = '0 0 30px rgba(255, 0, 255, 0.5)';
			}, 100);
		}
	}, 2000);
}

const form = document.querySelector('.newsletter-form');
if (form) {
	form.addEventListener('submit', (e) => {
		e.preventDefault();
		const button = e.target.querySelector('button');
		const originalText = button.textContent;
		button.textContent = 'Expanding...';
		button.style.background = 'linear-gradient(45deg, #00ff41, #0066ff)';
		setTimeout(() => {
			button.textContent = 'Welcome to the Cosmos! ✨';
			setTimeout(() => {
				button.textContent = originalText;
				button.style.background = 'linear-gradient(45deg, var(--neon-pink), var(--neon-blue))';
			}, 2000);
		}, 1500);
	});
}

function createParticle() {
	const particle = document.createElement('div');
	particle.style.position = 'fixed';
	particle.style.width = '4px';
	particle.style.height = '4px';
	particle.style.background = `hsl(${Math.random() * 360}, 100%, 50%)`;
	particle.style.borderRadius = '50%';
	particle.style.pointerEvents = 'none';
	particle.style.zIndex = '-1';
	particle.style.left = Math.random() * window.innerWidth + 'px';
	particle.style.top = window.innerHeight + 'px';
	particle.style.opacity = '0.7';
	document.body.appendChild(particle);
	const animation = particle.animate([
		{ transform: 'translateY(0px)', opacity: 0.7 },
		{ transform: `translateY(-${window.innerHeight + 100}px)`, opacity: 0 }
	], { duration: Math.random() * 3000 + 2000, easing: 'linear' });
	animation.onfinish = () => particle.remove();
}
setInterval(createParticle, 300);