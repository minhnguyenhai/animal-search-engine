$(document).ready(function () {
    function truncateText(text, maxLength = 200) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    function performSearch(query) {
        $('#results-container').html('<p>Searching...</p>');
        
        $.ajax({
            url: '/search',
            method: 'GET',
            data: { q: query },
            success: function (data) {
                const resultsContainer = $('#results-container');
                resultsContainer.empty(); // Clear previous results
                if (!Array.isArray(data)) {
                    console.error('Invalid response format:', data);
                    resultsContainer.html('<p>Error: Invalid response format</p>');
                    return;
                }
                if (data.length === 0) {
                    resultsContainer.append('<p>No results found.</p>');
                } else {
                    data.forEach(result => {
                        const resultItem = `
                            <div class="result-item">
                                <a href="${result.url}" class="result-title">${result.title}</a></br>
                                <div class="url-wrapper">
                                    <a class="result-url" href="${result.url}">${result.url}</a>
                                </div>
                                <p class="result-description">${truncateText(result.description)}</p>
                            </div>
                        `;
                        resultsContainer.append(resultItem);
                    });
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error('Search error:', textStatus, errorThrown);
                console.error('Response:', jqXHR.responseText);
                $('#results-container').html('<p>An error occurred while fetching the search results. Please try again.</p>');
            }
        });
    }

    $('#search-form').on('submit', function (event) {
        event.preventDefault();
        const query = $('#search-input').val();
        if (query.trim() === '') {
            alert('Please enter a search term.');
            return;
        }

        // Thay đổi URL trên trình duyệt mà không cần load lại trang
        const newUrl = `${window.location.pathname}?q=${encodeURIComponent(query)}`;
        history.pushState({ query: query }, '', newUrl);
        
        performSearch(query);
    });

    //Lưu và thực hiện lại trạng thái của trang khi người dùng click vào nút back hoặc forward trên trình duyệt
    $(window).on('popstate', function(event) {
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('q');
        
        if (query) {
            $('#search-input').val(query);
            performSearch(query);
        } else {
            $('#results-container').empty();
            $('#search-input').val('');
        }
    });

    //Kiểm tra xem trên URL có query không, nếu có thì thực hiện tìm kiếm
    const urlParams = new URLSearchParams(window.location.search);
    const initialQuery = urlParams.get('q');
    if (initialQuery) {
        $('#search-input').val(initialQuery);
        performSearch(initialQuery);
    }
});
