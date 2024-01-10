"use client"
import Image from 'next/image'
import React, {useState, useEffect} from 'react'
import styles from './page.module.scss'

const Home: React.FC = () => {

  let name = 'Jared'
  const [age, setAge] = useState(0)
  
  return (
    <div>
      <div className={styles.name}>
      My name is {name}
      </div>
    </div>
  )
}

export default Home;