// src/components/ads/AdSlider.js
import React, { useState, useEffect } from 'react';

const AdSlider = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  
  const ads = [
    {
      id: 1,
      image: '/images/fake-ad-banner.png',
      link: 'https://www.instagram.com/yh._official?utm_source=ig_web_button_share_sheet&igsh=bHFlcHV1djFzdWt3',
      alt: '광고 1'
    },
    {
      id: 2,
      image: '/images/fake-ad-banner2.jpg',
      link: 'https://www.instagram.com/kimu.ys_1118/',
      alt: '광고 2'
    },
    {
      id: 3,
      image: '/images/ad-banner.jpg',
      link: 'https://simplistic-bugle-82e.notion.site/APPLES-1a42880953e681658098da15fe8af285?source=copy_link',
      alt: '광고 3'
    }
  ];

  // 자동 슬라이드 (5초마다)
  useEffect(() => {
    if (ads.length <= 1) return; // 광고가 1개면 자동 슬라이드 안함
    
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => 
        prevIndex === ads.length - 1 ? 0 : prevIndex + 1
      );
    }, 5000);

    return () => clearInterval(interval);
  }, [ads.length]);

  const goToSlide = (index) => {
    setCurrentIndex(index);
  };

  const goToPrevious = () => {
    setCurrentIndex(currentIndex === 0 ? ads.length - 1 : currentIndex - 1);
  };

  const goToNext = () => {
    setCurrentIndex(currentIndex === ads.length - 1 ? 0 : currentIndex + 1);
  };

  // 광고가 없으면 렌더링하지 않음
  if (!ads.length) return null;

  // 모든 경우에 슬라이더로 렌더링 (단일 광고도 포함)
  return (
    <div className="ad partner-section">
      <h4>광고</h4>
      
      <div className="ad-slider-wrapper">
        {/* 슬라이더 컨테이너 */}
        <div className="ad-slider-container">
          <div 
            className="ad-slider-track"
            style={{ transform: `translateX(-${currentIndex * 100}%)` }}
          >
            {ads.map((ad) => (
              <div key={ad.id} className="ad-slide">
                <a href={ad.link} target="_blank" rel="noopener noreferrer">
                  <div 
                    className="ad-banner-bg"
                    style={{ backgroundImage: `url(${ad.image})` }}
                    role="img"
                    aria-label={ad.alt}
                  />
                </a>
              </div>
            ))}
          </div>
        </div>

        {/* 네비게이션 버튼 - 광고가 2개 이상일 때만 */}
        {ads.length > 1 && (
          <>
            <button className="ad-nav-btn ad-prev-btn" onClick={goToPrevious}>
              &#8249;
            </button>
            <button className="ad-nav-btn ad-next-btn" onClick={goToNext}>
              &#8250;
            </button>
          </>
        )}
      </div>

      {/* 인디케이터 점들 - 광고가 2개 이상일 때만 */}
      {ads.length > 1 && (
        <div className="ad-indicators">
          {ads.map((_, index) => (
            <button
              key={index}
              className={`ad-indicator ${index === currentIndex ? 'active' : ''}`}
              onClick={() => goToSlide(index)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default AdSlider;