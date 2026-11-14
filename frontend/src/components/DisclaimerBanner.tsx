import React from "react";

export const DisclaimerBanner: React.FC = () => {
  return (
    <div className="disclaimer-banner" role="alert">
      <span>
        🛡️ <strong>Research Decision Support Prototype:</strong> Intended for clinical evaluation and peer review. Dosing decisions and contraindication overrides remain the sole legal responsibility of the licensed physician.
      </span>
    </div>
  );
};
