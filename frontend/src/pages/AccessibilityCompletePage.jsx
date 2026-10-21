import React, { useEffect, useRef, useState } from 'react'
import { Button, Result, Spin } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import api from '../api'
import useStore from '../store/useStore'

export default function AccessibilityCompletePage() {
  const navigate = useNavigate()
  const location = useLocation()
  const started = useRef(false)
  const [error, setError] = useState('')
  useEffect(() => {
    if (started.current) return
    started.current = true
    const handoff = new URLSearchParams(location.search).get('handoff')
    if (!handoff) { setError('缺少画像跳转凭据，请返回六题问卷重新提交。'); return }
    // No normal account credentials are copied from the guest questionnaire.
    api.post('/accessibility/handoff', { handoff }).then(({ data }) => {
      if (!data.completed || !data.access_token || !data.profile) throw new Error('画像尚未完成')
      const store = useStore.getState()
      store.clearChatHistory()
      store.setStudentId(data.student_id)
      store.setStudentName(data.student_name)
      store.setStudentProfile(data.profile)
      store.setRegisterDate(data.register_date)
      store.setQuestionnaireComplete(true)
      store.setToken(data.access_token)
      store.setCurrentStep(1)
      store.setLearningPath([])
      store.setResources({})
      store.setCurrentKp(null)
      store.setPendingKpId(null)
      store.setPendingChapterId(null)
      store.setMasteryData({})
      store.setProgress(0)
      store.setGapCount(0)
      store.setDueReviewCount(0)
      useStore.setState({ user: { name: data.student_name }, course: data.profile.course })
      navigate('/dashboard', { replace: true })
    }).catch((err) => setError(err.response?.data?.detail || err.message || '载入失败，请重新提交问卷。'))
  }, [location.search, navigate])
  return <main style={{ padding: 40, textAlign: 'center' }}>
    {error ? <Result status="error" title="暂时无法进入主界面" subTitle={error}
      extra={<Button onClick={() => navigate('/accessibility', { replace: true })}>返回六题画像</Button>} />
      : <Spin tip="正在载入你的个性化画像…"><div style={{ height: 160 }} /></Spin>}
  </main>
}
