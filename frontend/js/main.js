document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // 1. Lógica de Pestañas (Tabs)
    // ==========================================
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remover activo de todos
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Activar actual
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // ==========================================
    // 2. Lógica de Drag & Drop y Subida de Archivo
    // ==========================================
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('csvFileInput');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const uploadBtn = document.getElementById('uploadBtn');
    let selectedFile = null;

    // Abrir selector al hacer clic en cualquier parte de la zona
    dropZone.addEventListener('click', (e) => {
        if (e.target !== uploadBtn) {
            fileInput.click();
        }
    });

    // Prevenir comportamientos por defecto del navegador al arrastrar
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Añadir/quitar clase visual al arrastrar encima
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    // Capturar el archivo cuando se suelta
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    });

    // Capturar el archivo cuando se selecciona vía clic
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    // Lógica de validación
    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.name.endsWith('.csv')) {
                selectedFile = file;
                fileNameDisplay.textContent = `✅ Archivo listo: ${file.name}`;
                uploadBtn.disabled = false;
            } else {
                alert('⚠️ Formato inválido. Por favor, selecciona un archivo .csv');
                resetFileSelection();
            }
        }
    }

    function resetFileSelection() {
        selectedFile = null;
        fileInput.value = '';
        fileNameDisplay.textContent = '';
        uploadBtn.disabled = true;
    }

   uploadBtn.addEventListener('click', async (e) => {
        e.stopPropagation(); 
        if (!selectedFile) return;

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            uploadBtn.textContent = 'Procesando Agentes (Espere)...';
            uploadBtn.disabled = true;

            // LLAMADA REAL A TU BACKEND LOCAL
            const response = await fetch('http://127.0.0.1:8000/api/procesar-dataset', {
                method: 'POST',
                body: formData
                // No pongas 'Content-Type', el navegador lo calcula automático con FormData
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            
            fileNameDisplay.textContent = `🚀 ¡Pipeline finalizado!`;
            uploadBtn.textContent = 'Procesar Nuevo Dataset';
            uploadBtn.disabled = false;
            
            // Mover automáticamente a la pestaña del Mapa/Dashboard
            document.querySelector('[data-target="bivariado"]').click();

        } catch (error) {
            console.error('Error en la conexión:', error);
            fileNameDisplay.textContent = '❌ Error al conectar con FastAPI. Revisa la consola.';
            uploadBtn.textContent = 'Reintentar';
            uploadBtn.disabled = false;
        }
    });
        document.querySelector('[data-target="bivariado"]').addEventListener('click', async () => {
        const mapContainer = document.getElementById('heatmapContainer');
        mapContainer.innerHTML = '<p style="text-align:center;">Cargando análisis geoespacial...</p>';

        try {
            // LLAMADA REAL AL ENDPOINT DEL MAPA
            const response = await fetch('http://127.0.0.1:8000/api/datos-mapa');
            if (!response.ok) throw new Error('Error al cargar datos del mapa');
            
            const datosBackend = await response.json();
            
            // Aquí conectamos los datos del backend con la función gráfica
            // Supongamos que tu función renderHeatmap ahora acepta provincias y tasas
            if (window.renderHeatmap) {
                // Adaptamos la data del backend a lo que necesita el frontend
                window.renderHeatmap(datosBackend.provincias, datosBackend.tasas_homicidios);
            }

        } catch (error) {
            console.error(error);
            mapContainer.innerHTML = '<p style="color:red; text-align:center;">Error al conectar con el servidor para obtener el mapa.</p>';
        }
    });

}); 