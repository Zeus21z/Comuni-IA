document.addEventListener('DOMContentLoaded', () => {
    const svg = document.querySelector('.connection-svg');
    const syncsLogo = document.getElementById('syncs-logo');
    const developers = ['zeus', 'zahid', 'cristhian', 'mijail'];
    const colors = ['#ff00ff', '#00ffff', '#ffff00', '#ff0000'];

    if (!svg || !syncsLogo) {
        console.error('SVG container or SYNCS logo not found.');
        return;
    }

    const createLine = (devElement, color, index) => {
        const containerRect = svg.parentElement.getBoundingClientRect();
        const logoRect = syncsLogo.getBoundingClientRect();
        const devRect = devElement.getBoundingClientRect();

        const logoX = logoRect.left + logoRect.width / 2 - containerRect.left;
        const logoY = logoRect.top + logoRect.height / 2 - containerRect.top;
        const devX = devRect.left + devRect.width / 2 - containerRect.left;
        const devY = devRect.bottom - containerRect.top;

        // Crear el grupo para la línea y sus efectos
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');

        // Línea principal
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', devX);
        line.setAttribute('y1', devY);
        line.setAttribute('x2', logoX);
        line.setAttribute('y2', logoY);
        line.setAttribute('stroke', color);
        line.classList.add('connection-line', `line-pulse-${index + 1}`);
        
        // Efecto de "brillo" que viaja por la línea
        const glow = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        glow.setAttribute('r', '4');
        glow.setAttribute('fill', color);
        glow.classList.add('connection-glow', `glow-travel-${index + 1}`);
        
        // Calcular el path para la animación
        const pathLength = Math.sqrt(Math.pow(logoX - devX, 2) + Math.pow(logoY - devY, 2));
        glow.setAttribute('data-start-x', devX);
        glow.setAttribute('data-start-y', devY);
        glow.setAttribute('data-end-x', logoX);
        glow.setAttribute('data-end-y', logoY);
        
        // Partículas que flotan desde los devs hacia SYNCS
        for (let i = 0; i < 3; i++) {
            const particle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            particle.setAttribute('r', '2');
            particle.setAttribute('fill', color);
            particle.setAttribute('opacity', '0.6');
            particle.classList.add('connection-particle', `particle-${index + 1}-${i + 1}`);
            particle.setAttribute('data-start-x', devX);
            particle.setAttribute('data-start-y', devY);
            particle.setAttribute('data-end-x', logoX);
            particle.setAttribute('data-end-y', logoY);
            group.appendChild(particle);
        }
        
        group.appendChild(line);
        group.appendChild(glow);
        svg.appendChild(group);
        
        // Animar el brillo y las partículas
        animateGlow(glow, devX, devY, logoX, logoY, index);
        animateParticles(group, devX, devY, logoX, logoY, index);
    };

    const animateGlow = (glow, startX, startY, endX, endY, index) => {
        const duration = 2000; // 2 segundos
        const delay = index * 300; // Retraso escalonado
        let startTime = null;

        const animate = (timestamp) => {
            if (!startTime) startTime = timestamp - delay;
            const elapsed = timestamp - startTime;
            const progress = ((elapsed % duration) / duration);

            // Movimiento de ida y vuelta
            const easedProgress = progress < 0.5 
                ? 2 * progress * progress 
                : 1 - Math.pow(-2 * progress + 2, 2) / 2;

            const currentX = startX + (endX - startX) * easedProgress;
            const currentY = startY + (endY - startY) * easedProgress;

            glow.setAttribute('cx', currentX);
            glow.setAttribute('cy', currentY);

            requestAnimationFrame(animate);
        };

        requestAnimationFrame(animate);
    };

    const animateParticles = (group, startX, startY, endX, endY, index) => {
        const particles = group.querySelectorAll('.connection-particle');
        
        particles.forEach((particle, i) => {
            const duration = 3000 + i * 500; // Diferentes velocidades
            const delay = index * 400 + i * 600;
            let startTime = null;

            const animate = (timestamp) => {
                if (!startTime) startTime = timestamp - delay;
                const elapsed = timestamp - startTime;
                const progress = ((elapsed % duration) / duration);

                const currentX = startX + (endX - startX) * progress;
                const currentY = startY + (endY - startY) * progress;

                // Agregar un pequeño movimiento ondulatorio
                const wave = Math.sin(progress * Math.PI * 4) * 5;
                const perpX = -(endY - startY) / Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
                const perpY = (endX - startX) / Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));

                particle.setAttribute('cx', currentX + perpX * wave);
                particle.setAttribute('cy', currentY + perpY * wave);
                
                // Fade in/out
                const opacity = progress < 0.1 ? progress * 10 : progress > 0.9 ? (1 - progress) * 10 : 1;
                particle.setAttribute('opacity', opacity * 0.6);

                requestAnimationFrame(animate);
            };

            requestAnimationFrame(animate);
        });
    };

    const drawLines = () => {
        svg.innerHTML = '';
        
        // Añadir filtro de brillo al SVG
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
        filter.setAttribute('id', 'glow');
        
        const feGaussianBlur = document.createElementNS('http://www.w3.org/2000/svg', 'feGaussianBlur');
        feGaussianBlur.setAttribute('stdDeviation', '3');
        feGaussianBlur.setAttribute('result', 'coloredBlur');
        
        const feMerge = document.createElementNS('http://www.w3.org/2000/svg', 'feMerge');
        const feMergeNode1 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode');
        feMergeNode1.setAttribute('in', 'coloredBlur');
        const feMergeNode2 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode');
        feMergeNode2.setAttribute('in', 'SourceGraphic');
        
        feMerge.appendChild(feMergeNode1);
        feMerge.appendChild(feMergeNode2);
        filter.appendChild(feGaussianBlur);
        filter.appendChild(feMerge);
        defs.appendChild(filter);
        svg.appendChild(defs);

        setTimeout(() => {
            developers.forEach((devId, index) => {
                const devElement = document.getElementById(`dev-${devId}`);
                if (devElement) {
                    createLine(devElement, colors[index], index);
                }
            });
        }, 100);
    };

    // Añadir efecto de pulso al logo SYNCS cuando las líneas se conectan
    const addLogoChargingEffect = () => {
        syncsLogo.style.filter = 'drop-shadow(0 0 10px currentColor)';
        
        setInterval(() => {
            const randomColor = colors[Math.floor(Math.random() * colors.length)];
            syncsLogo.style.textShadow = `0 0 20px ${randomColor}, 0 0 40px ${randomColor}`;
        }, 500);
    };

    drawLines();
    addLogoChargingEffect();

    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(drawLines, 250);
    });
});