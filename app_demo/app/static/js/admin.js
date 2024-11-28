var using_index

document.addEventListener('DOMContentLoaded', function() {
    fetch('/admin/indexes')
        .then(response => response.json())
        .then(data => {
            const firstIndex = data[0]; // Lưu phần tử đầu
            using_index = firstIndex;
            const remainingIndexes = data.slice(1);
            console.log('First index:', firstIndex);
            console.log('Remaining indexes:', remainingIndexes);
            const indexList = document.getElementById('index-list');
            indexList.innerHTML = '';
            remainingIndexes.forEach(index => {
                indexList.innerHTML += `<li>${index.name}</li>`;
                indexList.append(`<li>${index.count}</li>`)
            });
        })
        .catch(error => console.error('Error:', error));
});

$(document).ready(function () {
    // Tải danh sách Index
    $('#refresh-indexes').click(function () {
        $.get('/admin/indexes', function (data) {
            const firstIndex = data[0]; // Lưu phần tử đầu
            using_index = firstIndex;
            const remainingIndexes = data.slice(1);
            console.log('First index:', firstIndex);
            console.log('Remaining indexes:', remainingIndexes);
            
            const indexList = $('#index-list');
            const selectClientIndex = $('#select-index-search');
            const selectUploadIndex = $('#select-index-upload');

            indexList.empty();
            selectClientIndex.empty();
            selectUploadIndex.empty();

            remainingIndexes.forEach(index => {
                indexList.append(`<li>${index.name}</li>`);
                indexList.append(`<li>${index.count}</li>`)
                selectClientIndex.append(`<option value="${index.name}">${index.name}</option>`);
                selectUploadIndex.append(`<option value="${index.name}">${index.name}</option>`);
            });

            // Set default selected value if there are any indexes
            if (remainingIndexes.length > 0) {
                
                selectClientIndex.val(firstIndex.name);
                selectUploadIndex.val(firstIndex.name);
            }
        }).fail(() => alert("Không thể tải danh sách Index."));
    });

    // Tạo Index mới
    $('#create-index-form').submit(function (e) {
        e.preventDefault();
        const indexName = $('#index-name').val();
        const indexConfig = $('#index-config').val();
        $.ajax({
            url: '/admin/create-index',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ name: indexName, config: indexConfig }),
            success: () => {
                alert('Tạo index thành công.');
                $('#refresh-indexes').click();
            },
            error: () => alert('Lỗi khi tạo index.')
        });
    });

    // Đẩy Folder Data lên Index
    $('#upload-data-form').submit(function (e) {
        e.preventDefault();
        const indexName = $('#select-index-upload').val();
        const files = $('#data-folder')[0].files;
        const BATCH_SIZE = 50; // Số file trong mỗi batch
        
        if (files.length === 0) {
            alert('Vui lòng chọn một thư mục để upload');
            return;
        }

        if (!confirm(`Bạn có chắc chắn muốn upload ${files.length} files vào index "${indexName}"?`)) {
            return;
        }
        
        if (indexName !== using_index.name) {
            if (!confirm(`Bạn đang upload dữ liệu vào index "${indexName}" thay vì index đang dùng "${using_index.name}". Bạn có chắc chắn muốn tiếp tục?`)) {
                return;
            }
        }

        // Chia files thành các batch nhỏ hơn
        const batches = [];
        for (let i = 0; i < files.length; i += BATCH_SIZE) {
            batches.push(Array.from(files).slice(i, i + BATCH_SIZE));
        }

        let completedBatches = 0;
        const totalBatches = batches.length;

        // Hàm xử lý upload từng batch
        function uploadBatch(batchFiles, batchIndex) {
            const formData = new FormData();
            batchFiles.forEach(file => {
                formData.append('files', file);
            });

            return $.ajax({
                url: `/admin/upload-data/${indexName}`,
                method: 'POST',
                processData: false,
                contentType: false,
                data: formData,
                success: () => {
                    completedBatches++;
                    const progress = Math.round((completedBatches / totalBatches) * 100);
                    console.log(`Completed batch ${completedBatches}/${totalBatches} (${progress}%)`);
                    $('#refresh-indexes').click();
                },
                error: (xhr) => {
                    console.error(`Error uploading batch ${batchIndex + 1}:`, xhr.responseText);
                    throw new Error(`Failed to upload batch ${batchIndex + 1}`);
                }
            });
        }

        // Upload các batch tuần tự
        async function uploadAllBatches() {
            try {
                for (let i = 0; i < batches.length; i++) {
                    await uploadBatch(batches[i], i);
                }
                alert(`Upload thành công ${files.length} files.`);
                $('#refresh-indexes').click();
            } catch (error) {
                alert('Lỗi khi upload data: ' + error.message);
            }
        }

        uploadAllBatches();
    });

    // Thiết lập Index cho tìm kiếm client
    $('#set-client-index').click(function () {
        const indexName = $('#select-index-search').val();
        $.post('/admin/set-client-index', { index: indexName }, function () {
            alert('Đã thiết lập index cho tìm kiếm.');
        }).fail(() => alert('Lỗi khi thiết lập index cho client.'));
        $('#refresh-indexes').click();
    });

    // Tự động tải danh sách Index khi load trang
    $('#refresh-indexes').click();
});
