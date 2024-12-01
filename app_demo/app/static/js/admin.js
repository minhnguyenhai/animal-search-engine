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

            const indexList = $('#index-list');
            const selectClientIndex = $('#select-index-search');
            const selectUploadIndex = $('#select-index-upload');
            const selectConfigIndex = $('#select-index-config');

            indexList.empty();
            selectClientIndex.empty();
            selectUploadIndex.empty();
            selectConfigIndex.empty();

            remainingIndexes.forEach(index => {
                indexList.append(`<li>${index.name} (${index.count}) <button class="delete-index" data-index="${index.name}">Xoá</button></li>`);
                selectClientIndex.append(`<option value="${index.name}">${index.name}</option>`);
                selectUploadIndex.append(`<option value="${index.name}">${index.name}</option>`);
                selectConfigIndex.append(`<option value="${index.name}">${index.name}</option>`);
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
            const selectConfigIndex = $('#select-index-config');

            indexList.empty();
            selectClientIndex.empty();
            selectUploadIndex.empty();
            selectConfigIndex.empty();

            remainingIndexes.forEach(index => {
                indexList.append(`<li>${index.name} (${index.count}) <button class="delete-index" data-index="${index.name}">Xoá</button></li>`);
                selectClientIndex.append(`<option value="${index.name}">${index.name}</option>`);
                selectUploadIndex.append(`<option value="${index.name}">${index.name}</option>`);
                selectConfigIndex.append(`<option value="${index.name}">${index.name}</option>`);
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
        if (!indexName) {
            alert('Vui lòng nhập tên index.');
            return;
        }
        // nếu tên index có kí tự đặc biệt hoặc tiếng việt khoảng trắng thì báo lỗi
        if (!/^[a-z0-9_]+$/.test(indexName)) {
            alert('Tên index chỉ chứa các kí tự a-z, 0-9 và dấu gạch dưới.');
            return;
        }
        $.ajax({
            url: '/admin/create-index',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ indexName: indexName }),
            success: () => {
                alert('Tạo index thành công.');
                $('#refresh-indexes').click();
            },
            error: (xhr) => {
                console.error('Error creating index:', xhr.responseText);
                alert(`Lỗi khi tạo index: ${xhr.responseText}`);
            }
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

    // Xoá Index
    $(document).on('click', '.delete-index', function () {
        const indexName = $(this).data('index');
        if (confirm(`Bạn có chắc chắn muốn xoá index "${indexName}"?`)) {
            if (indexName === using_index.name) {
                alert('Không thể xoá index đang dùng.');
                return;
            }
            if(confirm(`Xác nhận lần nữa, bạn chắc chắn muốn xoá "${indexName}"? này?`)) {
                $.ajax({
                    url: `/admin/delete-index/${indexName}`,
                    method: 'DELETE',
                    success: () => {
                        alert('Xoá index thành công.');
                        $('#refresh-indexes').click();
                    },
                    error: () => alert('Lỗi khi xoá index.')
                });
            }
        }
    });

    // Xem c���u hình Index
    $('#view-index-config').click(function () {
        const indexName = $('#select-index-config').val();
        $.get(`/admin/index-config/${indexName}`, function (data) {
            $('#index-config-display').text(JSON.stringify(data, null, 2));
        }).fail(() => alert('Lỗi khi lấy cấu hình index.'));
    });

    // Popup functionality
    var popup = document.getElementById("create-index-popup");
    var btn = document.getElementById("create-index-button");
    var span = document.getElementsByClassName("close")[0];

    btn.onclick = function() {
        popup.style.display = "block";
    }

    span.onclick = function() {
        popup.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == popup) {
            popup.style.display = "none";
        }
    }

    // Tự động tải danh sách Index khi load trang
    $('#refresh-indexes').click();
});
