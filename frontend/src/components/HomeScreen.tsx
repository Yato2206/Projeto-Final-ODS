import React from "react"
import odsImage from "../assets/odsImage.png"

export function HomeScreen() {
    return (
        <div className="homescreen-container" style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            width: '100%'
        }}>
            <img
                src={odsImage}
                alt="ODS Image"
                style={{
                    maxWidth: '100%',
                    maxHeight: '100%',
                    width: 1200,
                    objectFit: 'contain',
                }}
            />
        </div>
    );
}

export default HomeScreen;