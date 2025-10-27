document.addEventListener('DOMContentLoaded', () => {
  const driver = window.driver.js.driver;

  const driverObj = driver({
    showProgress: true,
    steps: [
      { element: '.hero-section', popover: { title: 'Bienvenido a Comuni-IA', description: 'Tu plataforma para descubrir y potenciar emprendimientos locales con inteligencia artificial.' } },
      { element: '.search-card', popover: { title: 'Busca Negocios', description: 'Usa nuestro buscador para encontrar exactamente lo que necesitas. Puedes filtrar por nombre o categoría.' } },
      { element: '#business-grid', popover: { title: 'Emprendimientos Destacados', description: 'Explora los negocios más populares y novedosos de la comunidad.' } },
      { element: '#sobre', popover: { title: '¿Por qué Comuni-IA?', description: 'Descubre cómo ayudamos a los emprendedores a crecer y conectar con más clientes.' } },
      { element: '.navbar-main .btn-primary', popover: { title: 'Registra tu Negocio', description: '¿Tienes un negocio? Regístralo gratis y empieza a crecer con nosotros.', side: "left" } }
    ]
  });

  // No iniciar el tour automáticamente, esperar a que se haga clic en un botón
  // driverObj.drive(); 

  // Exponer el driver para poder iniciarlo desde otro sitio
  window.startTour = () => {
    driverObj.drive();
  };
});
