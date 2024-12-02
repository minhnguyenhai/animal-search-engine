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

    // Add upload type change handler
    $('input[name="upload-type"]').change(function() {
        if ($(this).val() === 'directory') {
            $('#data-folder').show();
            $('#data-file').hide();
        } else {
            $('#data-folder').hide();
            $('#data-file').show();
        }
    });

    // Replace both existing upload form submit handlers with this one
    $('#upload-data-form').submit(function (e) {
        e.preventDefault();
        const indexName = $('#select-index-upload').val();
        const uploadType = $('input[name="upload-type"]:checked').val();
        const files = uploadType === 'directory' ? $('#data-folder')[0].files : $('#data-file')[0].files;

        if (files.length === 0) {
            alert(uploadType === 'directory' ? 'Vui lòng chọn một thư mục để upload' : 'Vui lòng chọn một file JSON để upload');
            return;
        }

        if (!confirm(`Bạn có chắc chắn muốn upload ${uploadType === 'directory' ? files.length + ' files' : 'file ' + files[0].name} vào index "${indexName}"?`)) {
            return;
        }

        if (indexName !== using_index.name) {
            if (!confirm(`Bạn đang upload dữ liệu vào index "${indexName}" thay vì index đang dùng "${using_index.name}". Bạn có chắc chắn muốn tiếp tục?`)) {
                return;
            }
        }

        const formData = new FormData();
        formData.append('upload_type', uploadType);

        if (uploadType === 'directory') {
            // Handle directory upload
            const BATCH_SIZE = 50;
            const batches = [];
            for (let i = 0; i < files.length; i += BATCH_SIZE) {
                batches.push(Array.from(files).slice(i, i + BATCH_SIZE));
            }
            uploadAllBatches(batches, indexName, files.length);
        } else {
            // Handle single file upload
            formData.append('file', files[0]);
            alert('Chờ một chút nhé, đang xử lý file JSON...');
            $.ajax({
                url: `/admin/upload-data/${indexName}`,
                method: 'POST',
                processData: false,
                contentType: false,
                data: formData,
                success: (response) => {
                    alert(response.message);
                    $('#refresh-indexes').click();
                },
                error: (xhr) => {
                    alert('Lỗi khi upload data: ' + xhr.responseText);
                }
            });
        }
    });

    // Helper function for batch uploads
    async function uploadAllBatches(batches, indexName, totalFiles) {
        let completedBatches = 0;
        const totalBatches = batches.length;

        try {
            for (let i = 0; i < batches.length; i++) {
                await uploadBatch(batches[i], i, indexName);
                completedBatches++;
                console.log(`Completed batch ${completedBatches}/${totalBatches} (${Math.round((completedBatches / totalBatches) * 100)}%)`);
            }
            alert(`Upload thành công ${totalFiles} files.`);
            $('#refresh-indexes').click();
        } catch (error) {
            alert('Lỗi khi upload data: ' + error.message);
        }
    }

    function uploadBatch(batchFiles, batchIndex, indexName) {
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
            error: (xhr) => {
                console.error(`Error uploading batch ${batchIndex + 1}:`, xhr.responseText);
                throw new Error(`Failed to upload batch ${batchIndex + 1}`);
            }
        });
    }

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

    // Xem cấu hình Index
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
