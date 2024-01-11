"use client"
import Image from 'next/image'
import React, {useState, useEffect} from 'react'
import styles from './page.module.scss'

const Home: React.FC = () => {

  let name = 'Jared'
  const [age, setAge] = useState(0)
  
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        MLS Tracab GUI
      </div>
    </div>
  )
}

export default Home;