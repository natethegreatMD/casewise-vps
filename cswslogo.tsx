import React from 'react';
import type { IconProps } from '../types';

export const CasewiseLogo = (props: IconProps) => (
  <svg
    width="138px"
    height="28px"
    viewBox="0 0 138 28"
    version="1.1"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <g stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
      <g transform="translate(-74, -297)">
        <g transform="translate(74, 297)">
          <rect x="0" y="0" width="138" height="28" fill="none" />
          {/* Four-square grid similar to OHIF */}
          <g transform="translate(3, 3)" fill="#FFFFFF" stroke="#FFFFFF" strokeWidth="0.25">
            <rect x="0" y="0" width="9" height="9" rx="1" />
            <rect x="13" y="0" width="9" height="9" rx="1" />
            <rect x="0" y="13" width="9" height="9" rx="1" />
            <rect x="13" y="13" width="9" height="9" rx="1" />
          </g>

          {/* Text: CasewiseMD */}
          <text
            x="35"
            y="19"
            fontFamily="Segoe UI, Arial, sans-serif"
            fontSize="14"
            fontWeight="600"
            fill="#FFFFFF"
          >
            CasewiseMD
          </text>
        </g>
      </g>
    </g>
  </svg>
);

export default CasewiseLogo;
